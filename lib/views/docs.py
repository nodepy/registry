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

import collections
import os
import yaml
from flask import abort, request, render_template

import app from '../app'
import markdown from '../markdown'

basedir = os.path.join(app.root_path, '_vendor/nodepy/docs')
pages = require(os.path.join(basedir, '_pages.json'))


def find_page(path):
  def recursion(pages):
    for p in pages:
      if p['path'] == path: return p
      s = recursion(p.get('subs', []))
      if s: return s
    return None
  return recursion(pages)


@app.route('/docs')
@app.route('/docs/<path:path>')
def docs(path=None):
  # Find the active page.
  page = find_page(path)
  if not page: abort(404)

  filename = os.path.join(basedir, page['file'])
  with open(filename, 'r') as fp:
    md = markdown()
    content = md.convert(fp.read())

  return render_template('registry/docs.html',
    content=content, toc=md.toc, pages=pages, active_page=path, page=page)
