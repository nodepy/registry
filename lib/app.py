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
import jinja2
import json
import markdown
import os
from six.moves import urllib

manifest = require('nodepy-pm/lib/manifest')
models = require('./models')
resources = require('./resources')
utils = require('./utils')
markdown = require('./markdown')


app = flask.Flask('nodepy-registry', template_folder=os.path.join(__directory__, '../templates'))
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize the Jinja environment globals and filters..
app.jinja_env.globals.update({
  '__version__': str(manifest.parse(os.path.join(__directory__, '../package.json')).version),
  'active': lambda v, x: jinja2.Markup('class="active"') if v == x else '',
  'User': models.User,
  'Package': models.Package,
  'PackageVersion': models.PackageVersion,
  'resources': resources,
  'config': require('../config'),
  'jsonfmt': json.dumps,
  'urlparse': urllib.parse.urlparse,
  'url_for': utils.url_for,
  'active': utils.active
})

app.jinja_env.filters.update({
  'markdown': lambda x: markdown().convert(x),
  'sizeof_fmt': utils.sizeof_fmt,
  'pygmentize': utils.pygmentize
})

exports = app
