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
semver = require('@ppym/semver')


def expect_package_info(version_type=semver.Version, json=True):
  """
  Decorator for views that have a package and version parameter.
  """

  def decorator(func):
    @functools.wraps(func)
    def wrapper(package, version, *args, **kwargs):
      try:
        version = version_type(version)
      except ValueError as exc:
        if json:
          return response({'error': str(exc)}, 404)
        else:
          flask.abort(404)
      return func(package, version, *args, **kwargs)
    return wrapper
  return decorator


def json_catch_error():
  """
  Decorator to catch exceptions and turn them into JSON 500 responses.
  """

  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except Exception as exc:
        traceback.print_exc()
        if app.debug:
          return response({'error': str(exc)}, 500)
        else:
          return response({'error': "internal server error"}, 500)
    return wrapper
  return decorator


def on_return():
  """
  Passes an additional parameter at the beginning which is a list of callables
  that will be called after the function returns.
  """

  def decorator(func):
    handlers = []
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      try:
        return func(handlers, *args, **kwargs)
      finally:
        for handler in handlers:
          handler()
    return wrapper
  return decorator
