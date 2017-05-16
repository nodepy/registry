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
from flask import abort, render_template

app = require('../app')
basedir = os.path.join(app.root_path, '_vendor/nodepy/docs')

def _load_pages():
  Page = collections.namedtuple('Page', 'name path subs')
  configfn = os.path.join(app.root_path, '_vendor/nodepy/docs/pages.yml')
  with open(configfn) as fp:
    pages = yaml.load(fp)['pages']
  def convert(page):
    key, value = next(iter(page.items()))
    if isinstance(value, list):
      subs = [convert(c) for c in value]
      path = next((x for x in subs if x.path.endswith('index')), None)
      if path:
        subs.remove(path)
        path = path.path.rstrip('index').rstrip('/')
    else:
      subs = []
      path = value.rstrip('.md')
    return Page(key, path, subs)
  return [convert(c) for c in pages]

pages = _load_pages()


@app.route('/docs/')
@app.route('/docs/<path:path>')
def docs(path=''):
  filename = os.path.join(app.root_path, basedir, path)
  if os.path.isdir(filename):
    filename = os.path.join(filename, 'index.md')
  else:
    filename += '.md'
  if os.path.isfile(filename):
    with open(filename, 'r') as fp:
      return render_template('registry/docs.html',
        content=fp.read(), pages=pages, active_page=path)
  abort(404)
