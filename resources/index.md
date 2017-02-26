# PPY package registry

*Build Python applications the Node way.*

[PPY][ppy] is kind of a Node.js clone: An engine based on Python that lays the
foundation for loading Python modules resolved from actual filenames with a
`require()` function.

  [ppy]: https://github.com/ppym/engine

## Upload Packages

You have to register an account via the **ppym** command and then validate
your e-mail address in order to upload packages.

    $ ppym register --agree-tos
    $ ppym dist
    $ ppym upload dist/mypackage-1.0.0.tar.gz
