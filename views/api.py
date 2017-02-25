# Copyright (c) 2017 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import flask
import functools
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import traceback

from flask import request

config = require('../config')
app = require('../app')
httpauth = require('../httpauth')
decorators = require('../decorators')
models = require('../models')
manifest = require('@ppym/manifest')
semver = require('@ppym/semver')
registry_client = require('@ppym/ppym/registry')

User, Package, PackageVersion = models.User, \
    models.Package, models.PackageVersion


def response(data, code=200):
  return flask.Response(json.dumps(data), code, mimetype='test/json')


@app.route('/api/find/<package>/<version>')
@decorators.json_catch_error()
@decorators.expect_package_info(semver.Selector)
def find(package, version):
  def not_found(): return response({'status': 'package-not-found'}, 404)

  directory = os.path.join(config['registry.prefix'], package)
  print(directory)
  if not os.path.isdir(directory):
    return not_found()

  choices = []
  for have_version in os.listdir(directory):
    try:
      have_version = semver.Version(have_version)
    except ValueError as exc:
      app.logger.warn('invalid version directory found at "{}"'.format(
          os.path.join(directory, have_version)))
      continue
    if version(have_version):
      choices.append(have_version)

  if not choices:
    return not_found()

  choice = version.best_of(choices)
  directory = os.path.join(directory, str(choice))
  try:
    manifest = PackageManifest.parse(directory)
  except NotAPackageDirectory:
    app.logger.warn('missing package.json in "{}"'.format(directory))
    return not_found()
  except InvalidPackageManifest as exc:
    app.logger.warn('invalid package.json in "{}": {}'.format(directory, exc))
    return not_found()
  if manifest.name != package:
    app.logger.warn('"{}" lists unexpected package name "{}"'.format(
        manifest.filename, manifest.name))
    return not_found()
  if manifest.version != choice:
    app.logger.warn('"{}" lists unexpected version "{}"'.format(
        manifest.filename, manifest.version))
    return not_found()

  with open(manifest.filename) as fp:
    data = json.load(fp)
  data = {'status': 'ok', 'manifest': data}
  return response(data)


@app.route('/api/download/<package>/<version>/<filename>')
@decorators.expect_package_info(json=False)
def download(package, version, filename):
  """
  Note: Serving these files should usually be replaced by NGinx or Apache.
  """

  directory = os.path.join(config['registry.prefix'], package, str(version))
  directory = os.path.normpath(os.path.abspath(directory))
  return flask.send_from_directory(directory, filename)


@app.route('/api/upload/<package>/<version>', methods=['POST'])
@httpauth.login_required
@decorators.expect_package_info()
@decorators.json_catch_error()
@decorators.on_return()
def upload(on_return, package, version):
  user = User.objects(name=httpauth.username()).first()
  assert user
  if not user.validated:
    return response({'error': 'your email address is not verified'}, 403)

  # If the package already exists, make sure the user is authorized.
  has_package = Package.objects(name=package).first()
  owner = has_package.owner if has_package else None
  if owner and owner.name != httpauth.username():
    return response({'error': 'not authorized to manage package "{}", '
        'it belongs to "{}"'.format(package, owner.name)}, 400)

  force = request.args.get('force', 'false').lower().strip() == 'true'
  if len(request.files) != 1:
    return response({'error': 'zero or more than 1 file(s) uploaded'}, 400)

  filename, storage = next(request.files.items())
  if filename == 'package.json':
    return response({'error': '"package.json" can not be uploaded directly'}, 400)

  directory = os.path.join(config['registry.prefix'], package, str(version))
  absfile = os.path.join(directory, filename)
  if os.path.isfile(absfile) and not force:
    return response({'error': 'file "{}" already exists'.format(filename)}, 400)

  if filename == registry_client.get_package_archive_name(package, version):
    # Save the file to a temporary path because we can only read from the
    # FileStorage once.
    with tempfile.NamedTemporaryFile(suffix='_' + filename, delete=False) as tmp:
      shutil.copyfileobj(storage, tmp)
    on_return.append(tmp.delete)

    # Open the tar archive and read the package.json and README.md.
    with tarfile.open(tmp.name, mode='r') as tar:
      try:
        manifest_data = tar.extractfile('package.json').read().decode('utf8')
      except KeyError as exc:
        return response({'error': 'no `package.json` in the uploaded archive'}, 400)
      try:
        readme = tar.extractfile('README.md').read().decode('utf8')
      except KeyError:
        readme = None

    # Parse the manifest.s
    try:
      manifest = PackageManifest.parse_file(io.StringIO(manifest_data), directory)
    except InvalidPackageManifest as exc:
      return response({'error': 'invalid package manifest: {}'.format(exc)}, 400)
    if not manifest.license:
      return response({'error': 'packages on the registry must have a '
          '`license` defined in the manifest'}, 400)

    # Save the package.json into the directory.
    if not os.path.isdir(directory):
      os.makedirs(directory)
    with open(os.path.join(directory, 'package.json'), 'w') as fp:
      fp.write(manifest_data)

    # Copy the contents archive into the package version directory.
    shutil.copyfile(tmp.name, absfile)
  elif not os.path.isfile(os.path.join(directory, 'package.json')):
    return response({'error': 'package distribution must be uploaded before '
        'any additional files can be accepted'}, 400)
  else:
    manifest = None
    storage.save(absfile)

  # If the package doesn't belong to anyone, we'll add it to the user.
  if not owner:
    user = User.objects(name=httpauth.username()).first()
    has_package = Package(name=package, owner=user)
    has_package.save()
    print('Added package', package, 'to user', user.name)

  # Create the version if it doesn't exist already.
  pv = PackageVersion.objects(package=has_package, version=str(version)).first()
  if not pv:
    assert manifest
    pv = PackageVersion(package=has_package, version=str(version))
    print('Added version', manifest.version, 'to package', package)
  if manifest:
    pv.readme = readme
  pv.files.append(filename)
  pv.save()

  # Update the latest version if this one is newer than what we had
  # saved previously as the most recent version.
  if not has_package.latest or manifest.version > semver.Version(has_package.latest.version):
    has_package.latest = pv
    has_package.save()

  return response({'status': 'ok'})


@app.route('/api/register', methods=['POST'])
def register():
  username = request.form.get('username')
  password = request.form.get('password')
  email = request.form.get('email')
  if not username or len(username) < 3 or len(username) > 24:
    return response({'error': 'no or invalid username specified'}, 400)
  if not password or len(password) < 6 or len(password) > 64:
    return response({'error': 'no or invalid password specified'}, 400)
  if not email or len(email) < 4 or len(email) > 64:
    return response({'error': 'no or invalid email specified'}, 400)

  user = User.objects(name=username).first()
  if user:
    return response({'error': 'user "{}" already exists'.format(username)}, 400)
  if User.objects(email=email).first():
    return response({'error': 'email "{}" already in use'.format(email)}, 400)
  user = User(name=username, passhash=models.hash_password(password), email=email,
      validation_token=None, validated=False)

  if config['registry.require_email_verification'] == 'true':
    try:
      user.send_validation_mail()
    except ConnectionRefusedError as exc:
      app.logger.exception(exc)
      return response({'error': 'Verification e-mail could not be sent, the '
          'server\'s email settings may not be configured properly.'}, 503)
  else:
    user.validated = True
  user.save()

  message = 'User registered successfully.'
  if not user.validated:
    message += 'Please check your inbox for a verification e-mail.'
  if app.debug and not user.validated:
    message += ' DEBUG: Verify URL: {}'.format(user.get_validation_url())
  return response({'status': 'ok', 'message': message})
