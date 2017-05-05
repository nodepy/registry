<img src="https://i.imgur.com/IfmOKFI.png" align="right" width="150px"></img>

# PPYM registry

This is the PPYM registry server which is built entirely on [Node.Py]. It is
deployed on [ppym.org], which serves as the default PPYM registry. Node.Py and
the PPYM registry are currently in alpha development and are considered
unstable.

  [Node.Py]: https://github.com/nodepy/nodepy
  [PPYM]: https://github.com/nodepy/ppym
  [ppym.org]: https://ppym.org

__Requirements__

- [Node.Py] \*
- [MongoDB](https://www.mongodb.com/) \*
- [Kube CSS](https://imperavi.com/kube/)
- [Flask](http://flask.pocoo.org/)
- [Pygments](http://pygments.org/)

The PPYM registry is deployed on Python 3.6 and is also regularly tested on
Python 3.5. It may also run on other versions of Python (even Python 2.7), but
there is no guarantuee.

__Deployment__

Clone the repository, bootstrap the [PPYM] dependencies, then install the
dependencies of the registry server.

    $ nodepy ppym/bootstrap
    $ nodepy ppym install

After the dependencies have been installed, you can start the server.

    $ nodepy server

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
- User management API (change of password, email, etc. for the `ppym`
  command-line).

## Changelog

### v0.0.4

- Update page design with Kube CSS instead of Twitter Bootstrap
- Fix display of package description and license
- Add `manage promote` and `manage demote` commands
- Fix #1: TemplateNotFound when running the Flask app not from the project root
- Fix #2: Can not upload manifest containing . in a key
