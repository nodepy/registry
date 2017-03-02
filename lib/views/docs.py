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

from flask import abort, request, render_template
import os
import mkdocs.toc

app = require('../app')
markdown = require('../markdown')
docs_dir = os.path.normpath(os.path.join(__directory__, '../../docs'))


@app.route('/docs')
@app.route('/docs/<page>')
def docs(page='index'):
  # TODO: Disallow ../ parts in the page path.
  path = os.path.join(docs_dir, page + '.md')
  print(path)
  if not os.path.isfile(path):
    abort(404)

  md = markdown()
  with open(path) as fp:
    content = md.convert(fp.read())
  toc = mkdocs.toc.TableOfContents(md.toc)
  return render_template('registry/docs.html',
      nav='docs', content=content, toc=toc)
