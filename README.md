<img src="https://i.imgur.com/CdzJiFi.png" align="right" width="150px"></img>
# PPYM registry

This is the PPYM registry server which is built entirely on [Node.py]. It is
deployed on [ppym.org], which serves as the default PPYM registry. Node.py and
the PPYM registry are currently in alpha development and are considered
unstable.

  [Node.py]: https://github.com/nodepy/nodepy
  [PPYM]: https://github.com/nodepy/ppym
  [ppym.org]: https://ppym.org

__Requirements__

- [Node.py] on Python 3.5+
- MongoDB

__Deployment__

Clone the repository and install the dependencies with [PPYM]. To make
deployment easier, PPYM is included as a Git submodule already.

    $ node.py ppym install

After the dependencies have been installed, you can start the server.

    $ node.py server

The PPYM registry server has a number of configuration values that can be
specified in the PPYM configuration file which is usually found at `~/.ppymrc`.
Check the `lib/config.py` module in this repository for a list of all available
configuration values.

This is how the PPYM registry is configured on [ppym.org]:

    registry.host=localhost
    registry.port=5000
    registry.visible.host=ppym.org
    registry.visible.url_scheme=https
    registry.debug=false
    registry.prefix=~/ppym-registry-data
    registry.email.origin=no-reply@ppym.org
    registry.email.smtp_host=localhost:25
    registry.email.smtp_ssl=true
    registry.email.require_verification=true
    registry.accept_registrations=false

__Todo__

- Test sending of emails (for user email verification)
- Frontend search functionality
- Command-line to update existing users (eg. promote them to superusers)
- User management API (change of password, email, etc. for the `ppym`
  command-line).
