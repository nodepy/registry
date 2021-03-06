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

import os
import yaml
from flask import abort, redirect, request, render_template, Response

import app from '../app'
import models, {User, Package, PackageVersion} from '../models'
import refstring from '@nodepy/nppm/lib/refstring'


@app.route('/')
def index():
  return render_template('registry/index.html', nav='index')


@app.route('/info')
def info():
  return render_template('registry/info.html', nav='index')


@app.route('/browse')
@app.route('/browse/package/<package>')
@app.route('/browse/package/@<scope>/<package>')
@app.route('/browse/package/<package>/<version>')
@app.route('/browse/package/@<scope>/<package>/<version>')
def __browse_packages_backwards_compat(**kwargs):
  return redirect(request.path.replace('/package', '').replace('/browse', '/packages'))


@app.route('/browse/users')
@app.route('/browse/users/<user>')
def __browse_users__backwards_compat(**kwargs):
  return redirect(request.path.replace('/browse', ''))


@app.route('/packages')
def packages():
  return render_template('registry/browse/index.html', nav='packages')


@app.route('/packages/<package>')
@app.route('/packages/@<scope>/<package>')
@app.route('/packages/<package>/<version>')
@app.route('/packages/@<scope>/<package>/<version>')
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
      package=package, version=version, nav='packages')


@app.route('/users')
def users():
  return render_template('registry/browse/users.html', nav='users')


@app.route('/users/<user>')
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
