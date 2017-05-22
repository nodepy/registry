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
import shutil
import sys

import models from './lib/models'
import semver from 'nppm/lib/semver'
import refstring from 'nppm/lib/refstring'
import config from './config'


def prompt(question):
  while True:
    reply = input('{} [y/n] '.format(question)).strip().lower()
    if reply in ('yes', 'y'):
      return True
    elif reply in ('no', 'n'):
      return False
    print('Please reply with Yes or No.')


@click.group()
def main(): pass


@main.command()
@click.option('--all', is_flag=True, help='Drop everything we have.')
@click.option('-p', '--package', help='Drop a package and the selected versions from the registry.')
@click.option('-u', '--user', help='Drop a user from the registry, reowning his/her packages.')
@click.option('--reown', help='The name of the packages new owner when dropping a user.')
@click.option('--yes', is_flag=True, help='Don\'t ask for confirmation.')
@click.option('--keep-files', is_flag=True, help='Keep the files in the registry data directory.')
def drop(all, package, user, reown, yes, keep_files):
  """
  Drop the registry data, a specific package or user.
  """

  if all:
    if not yes and not prompt('Are you sure you want to drop all data?'):
      sys.exit(0)
    print('Dropping collection: user')
    models.User.drop_collection()
    print('Dropping collection: package')
    models.Package.drop_collection()
    print('Dropping collection: package_version')
    models.PackageVersion.drop_collection()
    print('Dropping collection: migration_revision')
    models.MigrationRevision.drop_collection()
    if not keep_files:
      print('Deleting registry data directory ...')
      if os.path.isdir(config.prefix):
        shutil.rmtree(config.prefix)
    sys.exit(0)

  if package:
    ref = refstring.parse(package)
    package = models.Package.objects(name=str(ref.package)).first()
    if not package:
      print('Package "{}" does not exist.'.format(ref.package))
      sys.exit(1)
    versions = []
    for pkgv in models.PackageVersion.objects(package=package):
      if not ref.version or ref.version(semver.Version(pkgv.version)):
        versions.append(pkgv)
    if ref.version and not versions:
      print('No versions matching "{}@{}"'.format(ref.package, ref.version))
      sys.exit(1)
    if ref.version:
      if yes:
        print('Dropping the following versions of "{}"'.format(ref.package))
      else:
        print('Are you sure you want to drop the following versions of "{}"?'
            .format(ref.package))
      for pkgv in versions:
        print('  -', pkgv.version)
      if not yes and not prompt('Confirm? '):
        sys.exit(0)
      print('Dropping "{}@{}" ...'.format(ref.package, ref.version))
    else:
      if not yes and not prompt('Do you really want to drop "{}" and all its versions?'
          .format(ref.package)):
        sys.exit(0)
      print('Dropping "{}" ...'.format(ref.package))

    for pkgv in versions:
      directory = pkgv.get_directory()
      pkgv.delete()
      if not keep_files:
        try:
          shutil.rmtree(directory)
        except OSError as exc:
          print('  Warning: error deleting files for "{}@{}": {}'
              .format(ref.package, pkgv.version, exc))
          continue

    if not ref.version:
      directory = package.get_directory()
      package.delete()
      if not keep_files:
        try:
          shutil.rmtree(directory)
        except OSError as exc:
          print('  Warning: error deleting files for "{}": {}'
              .format(ref.package, exc))
      sys.exit(0)

  if user:
    user_obj = models.User.objects(name=user).first()
    if not user_obj:
      print('User "{}" does not exist.'.format(user))
      sys.exit(1)
    if not yes and not prompt('Do you really want to drop user "{}"?'.format(user)):
      sys.exit(0)

    packages = models.Package.objects(owner=user_obj).all()
    if not reown and packages:
      reown = input('Which user should the {} packages be transfered to? '.format(len(packages)))
    if reown:
      reown_obj = models.User.objects(name=reown).first()
      if not reown_obj:
        print('User "{}" does not exist'.format(reown))
        sys.exit(1)
      if reown_obj == user_obj:
        print('Target user can not match the user that will be dropped.')
        sys.exit(1)
    if packages and not reown:
      print('Please specify a user the will own the users packages with --reown')
      sys.exit(1)

    if packages:
      print('Transferring packages ...')
    for package in packages:
      package.owner = reown_obj
      package.save()

    print('Dropping user "{}" ...'.format(user))
    user_obj.delete()
    sys.exit(0)


@main.command()
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-e', '--email')
@click.option('--superuser', is_flag=True)
@click.option('--verified', is_flag=True)
def adduser(username, password, email, superuser, verified):
  """
  Adds a user to the registry.
  """

  if not username:
    username = input('Username? ')
  if models.User.objects(name=username).first():
    print('User {} already exists'.format(username))
    return 1

  if not password:
    password = input('Password? ')
    if input('Confirm Password? ') != password:
      print('passwords do not match')

  if not email:
    email = input('Email? ')
  if models.User.objects(email=email).first():
    print('Email {} already in use'.format(email))
    return 1

  user = models.User(username, models.hash_password(password), email,
      superuser=superuser, validated=verified)
  user.save()
  print('User created.')


@main.command()
@click.argument('username')
def promote(username):
  """
  Promotes a user as superuser.
  """

  user = models.User.objects(name=username).first()
  if not user:
    print('User "{}" does not exist.'.format(username))
    return 1
  if not user.superuser:
    user.superuser = True
    user.save()
    print('User "{}" promoted.'.format(username))
    return 0
  else:
    print('User "{}" is already a superuser.'.format(username))
    return 1


@main.command()
@click.argument('username')
def demote(username):
  """
  Demotes a user from his/her superuser status.
  """

  user = models.User.objects(name=username).first()
  if not user:
    print('User "{}" does not exist.'.format(username))
    return 1
  if user.superuser:
    user.superuser = False
    user.save()
    print('User "{}" demoted.'.format(username))
    return 0
  else:
    print('User "{}" is not a superuser.'.format(username))
    return 1


@main.command()
@click.option('-d', '--dry', is_flag=True)
def migrate(dry):
  """
  Use after an update to upgrade the database.
  """

  migrate = require('./lib/migrate').Migration(models.db,
      models.CURRENT_REVISION, models.TARGET_REVISION,
      os.path.join(__directory__, 'lib/migrations'), dry=dry)
  migrate.execute()
  if not dry:
    models.MigrationRevision.set(models.TARGET_REVISION)


if require.main == module:
  main()
