<img src="https://i.imgur.com/IfmOKFI.png" align="right" width="150px"></img>

# nodepy/registry

This is the **nodepy package registry**  which is built entirely on [nodepy]
and deployed on [ppym.org]. It can be deployed locally for a private package
registry as well.

  [nodepy]: https://github.com/nodepy/nodepy
  [ppym.org]: https://ppym.org

## Requirements

- [nodepy] on Python 3.5+
- [MongoDB](https://www.mongodb.com/)
- [Kube CSS](https://imperavi.com/kube/) \*
- [Flask](http://flask.pocoo.org/) \*
- [Pygments](http://pygments.org/) \*

*\* Automatically installed*

## Installation & Deployment

Clone the repository with submodules. Install the dependencies with
**nodepy-pm**. The dependencies can be installed without connecting to
[ppym.org] as they are included as submodule.s

    $ git clone https://github.com/nodepy/registry.git --recursive
    $ cd registry
    $ nodepy-pm install

Update `config.py` and start the server.

    $ nodepy server

## Todolist

- Test sending of emails (for user email verification)
- Frontend search functionality
- User management API (change of password, email, etc. for the `nodepy-pm`
  command-line).

## Changelog

### 0.0.5

__General__

- rename from `ppym-registry` to just `registry` and package name to `@nodepy/registry`
- include `werkzeug-reloader-patch` and `nodepy` (which contains `nodepy-pm`
  as submodule
- configuration is now done in `config.py` instead of `~/.ppymrc`

__Template__

- Stick footer to bottom
- Show active page category by darker background in the menu
- Fix display of package description and license on the User page

### v0.0.4

- Update page design with Kube CSS instead of Twitter Bootstrap
- Fix display of package description and license
- Add `manage promote` and `manage demote` commands
- Fix #1: TemplateNotFound when running the Flask app not from the project root
- Fix #2: Can not upload manifest containing . in a key
