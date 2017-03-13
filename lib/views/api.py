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

from flask import request
from flask_restful import Resource, Api

fs = require('../fs')
config = require('../config')
resources = require('../resources')
app = require('../app')
httpauth = require('../httpauth')
decorators = require('../decorators')
models = require('../models')
manifest = require('ppym/lib/manifest')
semver = require('ppym/lib/semver')
refstring = require('ppym/lib/refstring')
registry_client = require('ppym/lib/registry')

User, Package, PackageVersion = models.User, \
    models.Package, models.PackageVersion


api = Api(app)


def _error(title, description, code):
  return {'error': {'title': title, 'description': description}}, code

def email_not_verified(user):
  return _error('Unauthroized access', 'Your email address is not verified', 403)

def unauthorized_access(user, pkg):
  return _error('Unauthroized access',
      'You do not have privileges to make changes to the '
        'package "{}"'.format(pkg.name),
      403)

def bad_request(description):
  return _error('Bad request', description, 400)

def service_unavailable(description):
  return _error('Serice unavailable', description, 503)


class FindPackage(Resource):

  def get(self, package, version, scope=None):
    package = str(refstring.Package(scope, package))
    try:
      version = semver.Selector(version)
    except ValueError as exc:
      flask.abort(404)

    # Check our database of available packages.
    package_obj = Package.objects(name=package).first()
    if not package_obj:
      return self.not_found(package, version)

    # Find a matching version.
    versions = PackageVersion.objects(package=package_obj)
    key = lambda x: semver.Version(x.version)
    best = version.best_of(versions, key=key)

    if not best:
      return self.not_found(package, version)

    try:
      return json.loads(best.manifest)
    except json.JSONDecodeError:
      app.logger.error("invalid manifest found: {}@{}".format(best.package.name, best.version))
      flask.abort(505)

  def not_found(self, package, version):
    return {'error': {
      'title': 'Package not found',
      'description': 'No package matching "{}@{}" could be found in the '
          'registry.'.format(package, version)
    }}, 404



class Download(Resource):
  """
  Note: Serving files should usually be performed by a real web server like
  NGinx or Apache. This API call is only available for development purposes.
  """

  def get(self, package, version, filename, scope=None):
    package = str(refstring.Package(scope, package))
    directory = os.path.join(config['registry.prefix'], package, version)
    directory = os.path.normpath(os.path.abspath(directory))
    return flask.send_from_directory(directory, filename)


class Upload(Resource):

  @httpauth.login_required
  @decorators.finally_(True)
  def post(self, finally_, package, version, scope=None):
    try:
      # Just make sure the scope and package are valid.
      package = refstring.Package(scope, package)
      version = semver.Version(version)
    except ValueError:
      flask.abort(404)

    replies = []

    # Find the authenticated user. We should always get one because we
    # use the same mechanism in httpauth.
    user = User.objects(name=httpauth.username()).first()
    if not user.validated:
      return email_not_verified(user)

    if config['registry.enforce_user_namespaces'] == 'true' \
        and package.scope != user.name and not user.superuser:
      return bad_request('You can only upload packages into your own namespace. '
        ' Rename your package to "@{}/{}"'.format(user.name, package.name))

    # Find the package information in our database.
    pkg = Package.objects(name=str(package)).first()
    if pkg and pkg.owner != user:
      return unauthorized_access(user, pkg)
    pkgversion = PackageVersion.objects(package=pkg, version=str(version)).first()

    # We only expect 1 file to be uploaded per request.
    if len(request.files) != 1:
      return bad_request('zero or more than 1 file(s) uploaded')
    filename, storage = next(request.files.items())
    if filename == 'package.json':
      return bad_request('"package.json" can not be uploaded directly')

    # Get the directory and filename to upload the file to.
    directory = os.path.join(config['registry.prefix'], str(package), str(version))
    absfile = os.path.join(directory, filename)

    # Check if the upload should be forced even if the file already exists.
    force = request.args.get('force', 'false').lower().strip() == 'true'
    if os.path.isfile(absfile) and not force:
      return bad_request('file "{} already exists'.format(filename))

    # Handle package source distributions special: Unpack the package.json
    # and README.md file and store the information in the database.
    if filename == registry_client.get_package_archive_name(package, version):
      # Save the uploaded file to a temporary path. Make sure it gets
      # deleted when we're done with the request.
      tmp = tempfile.NamedTemporaryFile(suffix='_' + filename, delete=False)
      tmp.close()
      finally_.append(lambda: fs.silentremove(tmp.name))
      storage.save(tmp.name)

      # Extract the package.json and README.md files.
      files = {}
      with tarfile.open(tmp.name, mode='r') as tar:
        for fn in ['package.json', 'README.md']:
          try:
            files[fn] = tar.extractfile(fn).read().decode('utf8')
          except KeyError:
            pass

      if 'package.json' not in files:
        return bad_request('The uploaded package distribution archive does '
            'not container a package.json file')

      # Parse the manifest.
      try:
        pkgmf_json = json.loads(files['package.json'])
        pkgmf = manifest.parse_dict(pkgmf_json)
      except (json.JSONDecodeError, manifest.InvalidPackageManifest) as exc:
        return bad_request('Invalid package manifest: {}'.format(exc))
      if not pkgmf.license:
        return bad_request('Packages uploaded to the registry must specify '
            'the `license` field.')
      if pkgmf.name != str(package) or pkgmf.version != version:
        return bad_request('The uploaded package distribution achive does '
            'not match with the target version. You are trying to uploaded '
            'the archive to "{}@{}" but the manifest says it is actually '
            '"{}".'.format(package, version, pkgmf.identifer))

      # Now that we validated the archive and its manifest, we can copy
      # it into our target directory.
      if not os.path.isdir(directory):
        os.makedirs(directory)
      shutil.move(tmp.name, absfile)

      # If the package did not exist yet, make sure it exists in the
      # database.
      if not pkg:
        replies.append('Added package "{}" to user "{}"'.format(package, user.name))
        pkg = Package(name=str(package), owner=user)
        pkg.save()

      # Same for the version.
      if not pkgversion:
        replies.append('Added new package version "{}"'.format(pkgmf.identifier))
        pkgversion = PackageVersion(package=pkg, version=str(version))
      else:
        replies.append('Updated package version "{}"'.format(pkgmf.identifier))
      pkgversion.readme = files.get('README.md', '')
      pkgversion.manifest = files['package.json']
      pkgversion.add_file(filename)
      pkgversion.save()

      # Update the 'latest' member in the Package.
      if pkg.update_latest(pkgversion):
        replies.append('{} is now the newest version of package "{}"'.format(
            pkgversion.version, pkg.name))

    # This does not appear to be a package distribution archive.
    # We only allow additional files after a distribution was uploaded
    # at least once.
    else:
      if not pkgversion:
        return bad_request('Additional file uploads are only allowed after '
            'a package distribution was uploaded at least once.')

      if os.path.isfile(absfile):
        replies.append('File "{}" updated.'.format(filename))
      else:
        replies.append('File "{}" saved.'.format(filename))

      # Simply save the file to the directory.
      storage.save(absfile)
      pkgmf = None
      pkgversion.add_file(filename)
      pkgversion.save()

    return {'message': '\n'.join(replies)}


class Register(Resource):

  def post(self):
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    if not username or len(username) < 3 or len(username) > 24:
      return bad_requests('No or invalid username specified')
    if not password or len(password) < 6 or len(password) > 64:
      return bad_requests('No or invalid password specified')
    if not email or len(email) < 4 or len(email) > 64:
      return bad_requests('No or invalid email specified')

    user = User.objects(name=username).first()
    if user:
      return bad_request('User "{}" already exists'.format(username))
    if User.objects(email=email).first():
      return bad_request('Email "{}" is already in use'.format(email))
    # TODO: Validate that `email` is a valid email address.

    if config['registry.accept_registrations'] != 'true':
      return bad_request('New user registrations are currently not accepted. '
          'Talk to the registry admin to manually create an account for you.')

    # Create the new user object.
    user = User(name=username, passhash=models.hash_password(password),
        email=email, validation_token=None, validated=False)

    if config['registry.email.require_verification'] != 'true':
      user.validated = True
    else:
      try:
        user.send_validation_mail()
      except ConnectionRefusedError as exc:
        app.logger.exception(exc)
        return service_unavailable('Verification e-mail could not be sent, '
            'the server\'s email settings may not be configured properly.')

    user.save()

    message = 'User registered successfully.'
    if not user.validated:
      message += ' Please check your inbox for a verification e-mail.'
    if app.debug and not user.validated:
      message += ' DEBUG: Verify URL: {}'.format(user.get_validation_url())

    return {'message': message}


class Terms(Resource):

  def get(self):
    # TODO: Add a "last-updated" field.
    return {'terms': resources.load('TERMS.txt')}


api.add_resource(FindPackage, '/api/find/<package>/<version>',
                              '/api/find/@<scope>/<package>/<version>')
api.add_resource(Download,    '/api/download/<package>/<version>/<filename>',
                              '/api/download/@<scope>/<package>/<version>/<filename>')
api.add_resource(Upload,      '/api/upload/<package>/<version>',
                              '/api/upload/@<scope>/<package>/<version>')
api.add_resource(Register,    '/api/register')
api.add_resource(Terms,       '/api/terms', endpoint='api_terms')
