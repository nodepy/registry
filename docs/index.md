Title: PPYM documentation
Summary: Documentation of Ppy and the Ppy Package Manager
Authors: Niklas Rosenstein
Date: March 1, 2017

<img src="https://i.imgur.com/W3652bU.png" align="right"></img>
# PPYM Documentation

PPYM is the package manager that comes pre-installed with [Ppy].

  [Ppy]: https://github.com/ppym/engine


## Command-line Interface

### `ppym init`

Initialize a `package.json` file in the current working directory.

### `ppym dist`

Create a `.tar.gz` archive from your package that can be uploaded to the
Ppy registry with [`ppym upload`](#ppym-upload).

### `ppym register`

Register a new account on the Ppy registry. Note that you can change the
URL to the registry being used in the `~/.ppyrc` file. By default, it will
point to https://ppym.org.

    $ craftr ~/.ppyrc
    registry=http://localhost:8000

### `ppym upload`

`ppym upload <filename>`

For the current version that is specified in the `package.json` of your
project, uploads the specified `<filename>` to the package registry. If the
version and/or package does not exist at the time of the upload, the file
will be rejected unless you upload the distribution archive created with
[`ppym dist`](#ppym-dist) first. If you upload the distribution archive, the
package and package version will be created and assigned to your account.

Note that on the global registry, packages you uploda must meet the following
requirements:

- The `name` of the package must be scoped with your username (ie. `@username/packagename`)
- The `license` field in `package.json` must not be empty

After a package version has been uploaded to the registry, arbitrary files
may be uploaded to that version as well. This is intended to be used for
additional files that may be downloaded by the actual package when necessary.
Note that https://ppym.org currently has a size upload limit of 2MiB.

**Read and understand the [Terms of Use](https://ppym.org/termms) before
uploading any content to the registry.**

### `ppym install`

`ppym install [-g]` (1)<br/>
`ppym install [-g] [-e] <directory>` (2)<br/>
`ppym install [-g] <filename>` (3)<br/>
`ppym install [-g] [@<scope>/]<package>` (4)

Installs a package (2, 3, 4) or the dependencies of the current package (1)
locally or globally (`-g, --global`). Local packages are installed into the
`ppy_modules/` directory. Scripts are placed into `ppy_modules/.bin/`, Python
modules installed via Pip are installed into `ppy_modules/.pymodules`.

### `ppym uninstall`

`ppym uninstall [-g] [@<scope>/]<package>`

Uninstalls a previously installed package.
