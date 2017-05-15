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

import errno
import os
import flask
import sass as libsass

def modified_after(subject, fn):
  return os.path.getmtime(subject) > os.path.getmtime(fn)

def convert(scss, css):
  """
  Converts the *scss* file to a *css* file.
  """

  try:
    with open(css, 'w') as fp:
      fp.write(libsass.compile(filename=scss))
  except Exception:
    try:
      os.remove(css)
    except OSError as exc:
      if exc.errno != errno.EOENT:
        raise
    raise

def sass(app, scss_dir='static/scss', css_dir='static/css',
         static_prefix='static/css', force=False):
  """
  Adds a URL rule that compiles the scss files from *scss_dir* into
  css files in *css_dir* if they are requested from the *static_prefix*.
  """

  @app.route('/%s/<path:filename>.css' % static_prefix)
  def sass_convert_route(filename):
    scss = os.path.join(scss_dir, filename + '.scss')
    css = os.path.join(css_dir, filename + '.css')
    if os.path.isfile(scss):
      if force or not os.path.isfile(css) or modified_after(scss, css):
        convert(scss, css)
    return flask.send_from_directory(*os.path.split(css))

exports = sass
