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
import sys

import config from './config'
import models from './lib/models'
import app from './lib/app'
import './lib/views/api'
import './lib/views/docs'
import './lib/views/registry'


def main():
  if models.CURRENT_REVISION is None:
    print('note: no database revision number found, assuming empty database.')
    models.CURRENT_REVISION = models.TARGET_REVISION
    models.MigrationRevision.set(models.TARGET_REVISION)
  elif models.CURRENT_REVISION != models.TARGET_REVISION:
    print('error: database not upgraded. The current revision is {} but '
        'we expected revision {}.'.format(models.CURRENT_REVISION,
          models.TARGET_REVISION))
    print('error: use the \'migrate\' command to upgrade the database.')
    sys.exit(1)

  app.run(host=config.host, port=config.port)


if require.main == module:
  main()
