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
import markupsafe
import pygments
import pygments.lexers
import pygments.formatters


def sizeof_fmt(num, suffix='B'):
  # http://stackoverflow.com/a/1094933/791713
  for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
    if abs(num) < 1024.0:
      return "%3.1f%s%s" % (num, unit, suffix)
    num /= 1024.0
  return "%.1f%s%s" % (num, 'Yi', suffix)


def url_for(*args, **kwargs):
  """
  A wrapper around #flask.url_for() that replaces escaped `@` symbols
  in the URL.
  """

  return flask.url_for(*args, **kwargs).replace('%40', '@')


def pygmentize(code, language):
  """
  """

  lexers = {
    'json': pygments.lexers.JsonLexer,
    'python': pygments.lexers.PythonLexer
  }
  fmt = pygments.formatters.HtmlFormatter(cssclass='codehilite')
  res = pygments.highlight(code, lexers[language](), fmt)
  return markupsafe.Markup(res)
