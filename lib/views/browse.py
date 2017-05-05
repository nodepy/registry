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

from flask import abort, request, render_template, Response

app = require('../app')
models = require('../models')
refstring = require('ppym/lib/refstring')

User, Package, PackageVersion = models.User, \
    models.Package, models.PackageVersion


@app.route('/')
def index():
  return render_template('registry/index.html', nav='index')


@app.route('/browse')
def browse():
  return render_template('registry/browse/index.html', nav='browse')


@app.route('/browse/package/<package>')
@app.route('/browse/package/@<scope>/<package>')
@app.route('/browse/package/<package>/<version>')
@app.route('/browse/package/@<scope>/<package>/<version>')
def package(package, scope=None, version=None):
  package = Package.objects(name=str(refstring.Package(scope, package))).first()
  if not package:
    abort(404)
  if version:
    version = PackageVersion.objects(package=package, version=version).first()
    if not version:
      abort(404)
  else:
    version = package.latest
  return render_template('registry/browse/package.html',
      package=package, version=version, nav='browse')


@app.route('/browse/users')
def users():
  return render_template('registry/browse/users.html', nav='users')


@app.route('/browse/users/<user>')
def user(user):
  user = User.objects(name=user).first()
  if not user:
    abort(404)
  return render_template('registry/browse/user.html', user=user, nav='users')


@app.route('/email/validate/<token>')
@app.route('/email/validate')
def validate_email(token=None):
  user = User.objects(validation_token=token).first()
  if not user or user.validated:
    abort(404)
  user.validated = True
  user.validation_token = None
  user.save()
  return render_template('registry/email/validated.html', user=user)


@app.route('/terms')
def terms():
  return render_template('registry/terms.html', nav='terms')


@app.errorhandler(404)
def page_not_found(e):
  return Response(render_template('registry/404.html'), 404)


@app.errorhandler(500)
def page_not_found(e):
  return Response(render_template('registry/500.html'), 500)


@app.route('/docs/latest')
def docs():
  """
  This route should be served by NGinx or Apache.
  """

  return "This route should be served by a real webserver."
