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
import json
import os
import uuid

from datetime import datetime
from hashlib import sha512
from mongoengine import *

import config from '../config'
import email from './email'
import semver from '@nodepy/nppm/lib/semver'
import licenses from '@nodepy/spdx-licenses'

# Note: if you experience extremly long load times, it might be because
# the mongo host can not be reached.
# TODO: Find out whether there is a timeout setting for connect().
db = connect(**config.mongodb)[config.mongodb['db']]


class User(Document):
  name = StringField(required=True, unique=True, min_length=3, max_length=64)
  passhash = StringField(required=True)
  email = StringField(required=True, min_length=4, max_length=54)
  created = DateTimeField(default=datetime.now)
  validation_token = StringField()
  validated = BooleanField(default=False)
  superuser = BooleanField(default=False)

  def send_validation_mail(self):
    """
    Sends an email with a email verification link. The user must be saved
    after this method is called. Note that this method can raise
    #ConnectionRefusedError if connecting to the SMTP server fails.
    """

    self.validation_token = str(uuid.uuid4())
    me = config.email['origin']
    html = flask.render_template('registry/email/validate-email.html', user=self)
    part = email.MIMEText(html, 'html')
    part['Subject'] = 'Validate your upmpy.org email'
    part['From'] = me
    part['To'] = self.email

    # Possible ConnectionRefusedError
    s = email.make_smtp()
    s.sendmail(me, [self.email], part.as_string())
    s.quit()

  def get_validation_url(self):
    return config.visible_url + flask.url_for(
      'validate_email', token=self.validation_token)

  def get_url(self):
    return flask.url_for('user', user=self.name)


class Package(Document):
  name = StringField(required=True, unique=True)
  owner = ReferenceField('User', DENY)
  latest = ReferenceField('PackageVersion', DENY)
  created = DateTimeField(default=datetime.now)

  def update_latest(self, version, save=True):
    assert isinstance(version, PackageVersion)
    assert version.package == self
    if not self.latest or semver.Version(version.version) > semver.Version(self.latest.version):
      self.latest = version
      if save:
        self.save()

  def get_directory(self):
    return os.path.join(config.prefix, self.name)

  def get_url(self):
    return flask.url_for('package', package=self.package.name)


class PackageVersion(Document):
  package = ReferenceField('Package', CASCADE)
  version = StringField(required=True, min_length=1)
  created = DateTimeField(default=datetime.now)
  files = ListField(StringField())
  readme = StringField()

  # Actually a JSON encoded string, but MongoDB does not allow dots in
  # documents, which may very well ocurr in package manifests.
  manifest = StringField()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._manifest_json = None

  @property
  def manifest_json(self):
    if self._manifest_json is None and self.manifest:
      try:
        self._manifest_json = json.loads(self.manifest)
      except json.JSONDecodeError:
        self._manifest_json = None
    return self._manifest_json

  @property
  def license(self):
    """
    Reads the license information from the manifest and returns a dictionary
    with the license information. Additionally to the standard fields "name",
    "identifier", "deprecated" and "osi_approved", it also contains a "url"
    field which points to the license description. The field is empty if the
    license identiifer in the manifest is unknown.
    """

    if not self.manifest_json:
      return None
    ident = self.manifest_json.get('license')
    if not ident:
      return None

    # TODO: Hashtable..?
    for lic in licenses:
      if lic['identifier'] == ident:
        break
    else:
      return {'name': ident, 'identifier': ident, 'deprecated': False,
              'osi_approved': False, 'url': None}

    lic = lic.copy()
    lic['url'] = 'https://spdx.org/licenses/{}.html'.format(lic['identifier'])
    return lic

  def add_file(self, filename):
    if filename not in self.files:
      self.files.append(filename)

  def get_directory(self):
    return os.path.join(self.package.get_directory(), self.version)

  def get_file_path(self, filename):
    return os.path.join(self.get_directory(), filename)

  def get_file_size(self, filename):
    path = self.get_file_path(filename)
    try:
      return os.path.getsize(path)
    except FileNotFoundError:
      return 0

  def get_url(self):
    return flask.url_for('package', package=self.package.name, version=self.version)


class MigrationRevision(Document):
  """
  Stores a single entity, that is the revision number of the database.
  """

  revision = IntField()

  @staticmethod
  def get():
    obj = MigrationRevision.objects().first()
    if obj is not None:
      return obj.revision
    return None

  @staticmethod
  def set(revision):
    obj = MigrationRevision.objects().first()
    if not obj:
      obj = MigrationRevision(revision)
    else:
      obj.revision = revision
    obj.save()
    assert MigrationRevision.get() == revision


def hash_password(password):
  return sha512(password.encode('utf8')).hexdigest()



CURRENT_REVISION = MigrationRevision.get()
TARGET_REVISION = 2  # Current revision number of our models.
