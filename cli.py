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

import click
import os

config = require('./config')
app = require('./app')
models = require('./models')
require('./views/api')
require('./views/browse')


@click.group()
def cli():
  pass


@cli.command()
@click.option('-h', '--host')
@click.option('-p', '--port', type=int)
@click.option('--debug/--no-debug', default=None)
@click.option('--prefix')
def run(host, port, debug, prefix):
  if models.CURRENT_REVISION != models.TARGET_REVISION:
    print('error: database not upgraded. The current revision is {} but '
        'we expected revision {}'.format(models.CURRENT_REVISION,
          models.TARGET_REVISION))
    print('error: use \'ppy-registry migrate\' to upgrade the database')
    return

  if host is None:
    host = config['registry.host']
  if port is None:
    port = int(os.getenv('', int(config['registry.port'])))
  if debug is None:
    debug = (config['registry.debug'].lower().strip() == 'true')
  if prefix is not None:
    config['registry.prefix'] = prefix

  if debug:
    # TODO: Support Werkzeug livereloader in ppy environments.
    #       See ppym/engine#6.
    print('note: Unfortunately, Flask debug mode (specifically livereload) '
        'is currently not supported in ppy environments.')
    debug = False

  app.run(host=host, port=port, debug=debug)


@cli.command()
def drop():
  reply = input('Do you really want to drop all data in the database? ')
  if reply  in ('y', 'yes'):
    print('Okay..')
    models.User.drop_collection()
    models.Package.drop_collection()
    models.PackageVersion.drop_collection()
  else:
    print('Better so.')


@cli.command()
@click.argument('from_', 'from')
@click.argument('to')
def testmail(from_, to):
  part = email.MIMEText('This is a test email')
  part['From'] = from_
  part['To'] = to
  part['Subject'] = 'Test email'
  s = email.make_smtp()
  s.sendmail(from_, [to], part.as_string())
  s.quit()


@cli.command()
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-e', '--email')
def adduser(username, password, email):
  if not username:
    username = input('Username? ')
  if not password:
    password = input('Password? ')
    if input('Confirm Password? ') != password:
      print('passwords do not match')
  if not email:
    email = input('Email? ')

  if models.User.objects(name=username).first():
    print('User {} already exists'.format(username))
    return 1
  if models.User.objects(email=email).first():
    print('Email {} already in use'.format(email))
    return 1

  user = models.User(username, models.hash_password(password), email)
  user.save()
  print('User created.')


@cli.command()
@click.option('-d', '--dry', is_flag=True)
def migrate(dry):
  """
  Use after an update to upgrade the database.
  """

  migrate = require('./migrate').Migration(models.db,
      models.CURRENT_REVISION, models.TARGET_REVISION,
      os.path.join(_dirname, 'migrations'), dry=dry)
  migrate.execute()
  if not dry:
    models.MigrationRevision.set(models.TARGET_REVISION)


if require.is_main:
  cli()
