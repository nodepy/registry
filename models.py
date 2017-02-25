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
import uuid

from datetime import datetime
from hashlib import sha512
from mongoengine import *

config = require('./config')
email = require('./email')

# Note: if you experience extremly long load times, it might be because
# the mongo host can not be reached.
# TODO: Find out whether there is a timeout setting for connect().
connect(
  db = config['registry.mongodb.db'],
  host = config['registry.mongodb.host'],
  port = int(config['registry.mongodb.port']),
  username = config['registry.mongodb.username'],
  password = config['registry.mongodb.password']
)


class User(Document):
  name = StringField(required=True, unique=True, min_length=3, max_length=64)
  passhash = StringField(required=True)
  email = StringField(required=True, min_length=4, max_length=54)
  created = DateTimeField(default=datetime.now)
  validation_token = StringField()
  validated = BooleanField()

  def send_validation_mail(self):
    """
    Sends an email with a email verification link. The user must be saved
    after this method is called.
    """

    self.validation_token = str(uuid.uuid4())
    me = config['upmd.email_origin']
    html = flask.render_template('validate-email.html', user=self)
    part = email.MIMEText(html, 'html')
    part['Subject'] = 'Validate your upmpy.org email'
    part['From'] = me
    part['To'] = self.email
    s = email.make_smtp()
    s.sendmail(me, [self.email], part.as_string())
    s.quit()

  def get_validation_url(self):
    res = config['upmd.visible_url_scheme'] + '://'
    res += config['upmd.visible_host']
    res += flask.url_for('validate_email', token=self.validation_token)
    return res


class Package(Document):
  name = StringField(required=True, unique=True)
  owner = ReferenceField('User', DENY)
  latest = ReferenceField('PackageVersion', DENY)
  created = DateTimeField(default=datetime.now)


class PackageVersion(Document):
  package = ReferenceField('Package', CASCADE)
  version = StringField(required=True, min_length=1)
  created = DateTimeField(default=datetime.now)
  files = ListField(StringField())
  readme = StringField()


def hash_password(password):
  return sha512(password.encode('utf8')).hexdigest()
