# Build awesome Python applications

### with Node.py

**Node.py** is a Python runtime layer that is inspired by **Node.js**. It
allows you to create modular, easily distributable and reproducible Python
applications in the **Node.js** style. Node.py comes batteries included with
its  package manager **nodepy-pm** which allows you to manage Node.py and
standard Python packages for your project. No virtualenv required!

Node.py is supported on all major platforms that [CPython] can run on. 

  [nodepy]: https://github.com/nodepy/nodepy
  [CPython]: https://python.org/

## Installing Node.py

You can install Node.py via Pip, which will also install nodepy-pm.

    $ pip install node.py

To get started, try something like this:

    $ nodepy-pm install @nodepy/hello
    $ nodepy @nodepy/hello
    Hello from Node.py!
    $ export PATH=$PATH:nodepy_modules/.bin
    $ nodepy-hello
    Hello from Node.py!

## Todo

- Implement search form (currently a placeholder)
- Caching for HTML content generated from Markdown
- Caching for CSS generated from SCSS
- Account management API (for the **nodepy-pm** command-line)
- Web-login and registration for users
- Option to require log-in to view registry content (useful for private registry hosting)
- Display TOC in Documentation pages
- Track download count of packages
- Ability to deprecate whole packages (and package manager will recieve this
  information via the API)
