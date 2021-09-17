.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

=======================
collective.patchwatcher
=======================

A great companion for keeping track of patched or overridden files.

It requires you to have installed the programs diff and diff3.

Features
--------

- declare your overriden files


Examples
--------

Assume your have overridden a file called "querywidget.pt" with jbot, which lives in your own theming package.
To make this explicit, you have to create a file called "overrides_info.py" which has to offer an importable variable "declarations".

It should contain the following content:

```
from collective.patchwatcher import DeclarationCollection

declarations = DeclarationCollection("your.theming.addon")

declarations.add(
    package="archetypes.querywidget",
    version="1.1.2",
    path="./skins/querywidget/querywidget.pt",
    local_path="./overrides/archetypes.querywidget.skins.querywidget.querywidget.pt",
)
# ... add more declarations as you wish.
```

These declarations states, that the overridden file refers to some file from
another package and has been tested against a specific version.

Then you can call this script to check all these declarations:

./bin/patchwatcher -e "/home/username/zinstance/eggs" -p your.theming.addon

Doing so will check, if the latest version (for example 1.1.4) of
archetypes.querywidget has changed the overriden file and if yes, it tries to
apply the changes in your overridden file.

Add "-m" if you want to save the result of the three-way merge. There may be
conflicts, which then have to be resolved manually.
You then may update the declaration to 1.1.4 in the "overrides_info.py",
basically saying that it's also compatible with this new version.

Documentation
-------------

Full documentation for end users can be found in the "docs" folder, and is also available online at http://docs.plone.org/foo/bar

Installation
------------

Install collective.patchwatcher by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.patchwatcher


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.patchwatcher/issues
- Source Code: https://github.com/collective/collective.patchwatcher
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.
