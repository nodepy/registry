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


class MigrationError(Exception):
  pass


class Migration(object):

  def __init__(self, db, current_revision, target_revision, migrations_dir, dry=False):
    if target_revision < current_revision:
      raise ValueError('target_revision must be >= current_revision')
    self.db = db
    self.current_revision = current_revision
    self.target_revision = target_revision
    self.migrations_dir = migrations_dir
    self.dry = dry

  def execute(self):
    if self.current_revision == self.target_revision:
      print('Nothing to be migrated.')
      return
    for i in range(self.current_revision, self.target_revision):
      filename = os.path.join(self.migrations_dir, '{:0>4}.py'.format(i+1))
      print('Running migration "{}" ...'.format(filename))
      self.execute_migration(filename)

  def execute_migration(self, filename):
    with open(filename, 'r') as fp:
      code = compile(fp.read(), filename, 'exec')
    scope = {'__file__': filename, 'migrate': self}
    exec(code, scope)

  def _check_collection(self, collection):
    if collection not in self.db.collection_names():
      print('    warning: Database has no collection "{}"'.format(collection))

  def add_field(self, collection, field, value):
    """
    Adds a field to a collection with the specified default value if the
    field does not already exist.
    """
    print('  Adding field "{}" to collection "{}" with value "{}"'.format(
        field, collection, value))
    self._check_collection(collection)
    if self.dry:
      print('    Skipped (dry run)')
    else:
      result = self.db[collection].update({}, {'$set': {field: value}})
      print('    {}'.format(result))

  def delete_field(self, collection, field):
    """
    Removes a field from all documents in a collection.
    """

    print('  Deleting field "{}" of collection "{}"'.format(field, collection))
    self._check_collection(collection)
    if self.dry:
      print('    Skipped (dry run)')
    else:
      result = self.db[collection].update({}, {'$unset': {field: 1}})
      print('    {}'.format(result))
