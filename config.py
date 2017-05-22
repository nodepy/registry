# Configuration file for the nodepy registry server.

import os
from urllib.parse import urlparse

# The host and port on which the application server is started.
# localhost should be used when deploying for the local machine only,
# otherwise use a static IP address, 0.0.0.0 or a domain name.
host = 'localhost'
port = 8000

# The visible url of the application. This url is used for example in
# the mail sent to verify your email address after registering an account.
visible_url = 'http://{}:{}'.format(host, port)
server_name = urlparse(visible_url).netloc

# Run in debug mode.
debug = True

# The prefix under which the application data is stored.
prefix = os.path.expanduser('~/nodepy-registry-data')

# Mongo DB connection settings.
mongodb = {
  'host': 'localhost',
  'port': 27017,
  'db': 'nodepy_registry',
  'username': None,
  'password': None
}

# Email configuration.
email = {
  'origin': 'no-reply@{}'.format(server_name.partition(':')[0]),
  'smtp_host': 'localhost:25',
  'smtp_ssl': False
}

# True if email verification is required when registering an account.
require_email_verification = True

# True if package names must be scoped in the uploaders username and
# otherwise reject the package (superusers can still upload any package).
enforce_package_namespaces = True

# True if new registrations are accepted. If this is set to False, a notice
# will be displayed on the webpage and new registrations will be rejected.
accept_registrations = True

# Site title.
site_title = 'nodepy/registry'

# A Google Analytics ID.
google_analytics = None
