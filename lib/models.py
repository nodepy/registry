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

config = require('./config')
email = require('./email')
semver = require('ppym/lib/semver')

# Note: if you experience extremly long load times, it might be because
# the mongo host can not be reached.
# TODO: Find out whether there is a timeout setting for connect().
db = connect(
  db = config['registry.mongodb.db'],
  host = config['registry.mongodb.host'],
  port = int(config['registry.mongodb.port']),
  username = config['registry.mongodb.username'],
  password = config['registry.mongodb.password'],
)[config['registry.mongodb.db']]


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
    me = config['registry.email.origin']
    html = flask.render_template('validate-email.html', user=self)
    part = email.MIMEText(html, 'html')
    part['Subject'] = 'Validate your upmpy.org email'
    part['From'] = me
    part['To'] = self.email

    # Possible ConnectionRefusedError
    s = email.make_smtp()
    s.sendmail(me, [self.email], part.as_string())
    s.quit()

  def get_validation_url(self):
    res = config['registry.visible.url_scheme'] + '://'
    res += config['registry.visible.host']
    res += flask.url_for('validate_email', token=self.validation_token)
    return res

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
    return os.path.join(config['registry.prefix'], self.name)

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
    try:
      self.manifest_json = json.loads(self.manifest)
    except json.JSONDecodeError:
      self.manifest_json = None

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
