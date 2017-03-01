<img src="https://i.imgur.com/W3652bU.png" align="right"></img>
# @ppym/registry

This is the PPYM registry server which is built entirely on [Ppy]. It is
deployed on [ppym.org], which serves as the default Ppy registry. Ppy and
the Ppy registry are currently in alpha development and are considered
unstable. For more information on Ppy, check out the [@ppym/engine][ppy]
repository.

  [ppy]: https://github.com/ppym/engine
  [ppym.org]: https://ppym.org

__Requirements__

- [Ppy] on Python 3.5 or newer
- MongoDB

__Deployment__

Clone the repository and install the `@ppym/registry` package in develop mode.
This will install all dependencies into a `ppy_modules/` directory, including
the standard Python modules. After that, you can run the server.

There are a number of configuration values that can be defined in the
`~/.ppyrc` file. Check out the `config.py` file in this repository for the
available values and their default values.

    $ git clone https://github.com/ppym/registry.git ppy-registry
    $ cd ppy-registry
    $ ppym install -e .
    $ ppy_modules/.bin/ppy-registry run

__Todo__

- Test sending of emails (for user email verification)
- Frontend search functionality
- Command-line to update existing users (eg. promote them to superusers)
- User management API (change of password, email, etc. for the `ppym`
  command-line).
