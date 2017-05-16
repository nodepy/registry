<img src="https://i.imgur.com/IfmOKFI.png" align="right" width="150px"></img>

## The **Node.py** Package Registry

  [nodepy]: https://github.com/nodepy/nodepy

Welcome to the nodepy package registry, the repository for [nodepy] packages.
**nodepy** is a Python runtime layer that is inspired by **Node.js**. It
allows you to create well structured, easily distributable and reproducible
Python applications.

### Key Features of Node.py

- The power of *Node.js*'s `require()` in Python
- Compatible with Python 2.7 and 3.3+
- Batteries included: the **nodepy-pm** package manager allows you to install
  and manage dependencies
- Standard Python modules are supported and it is *encouraged* to use them

### Installation

You can install **nodepy** via Pip. This will automatically install the
`nodepy` and `nodepy-pm` commands.

    $ pip install node.py

If you pass the `--user` option, make sure that the user scripts directory
is in your `PATH` (eg. `~/.local/bin` on Linux, `~/.local/Scripts` or
`~/AppData/Local/Programs/Python/PythonX.Y/Scripts` on Windows).

It is also recommended to add the path `nodepy_modules/.bin` to your
`PATH` environment variables, so that you will be able to run scripts
installed locally via **nodepy-pm**.

    $ echo 'export PATH="PATH:nodepy_modules/.bin"' >> ~/.profile

### Todo

- Implement package search functionality (currently the form in the sidebar
  is only a placeholder)
- Caching for HTML generated from Markdown (especially the main and
  documentation pages)
- Generate CSS from SASS on startup in production mode
- \+ everything else listed in the [Issue Tracker](https://github.com/nodepy/registry/issues)