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

- provide an easy way to declare your overriden files for your package (including version of the dependencies)
- automatically check the declarations of a package for version updates of the dependencies
- automatically merge version updates into your overrides
- additionally use your declarations to add version pins for the dependencies in the setup.py of your package


Examples
--------

Assume you have overridden a file called "querywidget.pt" with jbot in your own package called "my.package" in a folder called "overrides" (the default way to do this).
The file is orginally provided by archetypes.querywidget and lives in the Folder "skins/querywidget/" of that package. When you created the override, archetypes.querywidget version 1.1.2 was installed.
To make this explicit, you have to create a file called "overrides_info.py" inside your package namespace which has to offer an importable variable "declarations".

It should contain the following content:

.. code-block:: python

    from collective.patchwatcher import DeclarationCollection

    declarations = DeclarationCollection()

    declarations.add(
        package="archetypes.querywidget",
        version="1.1.2",
        path="./skins/querywidget/querywidget.pt",
        local_path="./overrides/archetypes.querywidget.skins.querywidget.querywidget.pt",
    )
    # add more declarations as you wish

The declaration states the original package, version and relative file path as well as the local path to your override.

Now you can call the patchwatcher script to check your declarations for your package
after you potentially updated its dependency packages (e.g. by updating your Plone version):

.. code-block:: console

    ./bin/patchwatcher -e "/home/username/zinstance/eggs" -p my.package

Patchwatcher needs the path to your eggs directory to find the latest version (in our example version 1.1.4) of
archetypes.querywidget. It will look for changes between both orginal files in versions 1.1.2 and 1.1.4.
Note, that this is only possible if both versions are present in the eggs directory.
This is usually the case, when you just updated your version pins and freshly ran buildout.
If patchwatcher finds changes, it will try to apply the changes to your overridden file using a three-way-merge.

Add the "-w" option to the script invocation if you want to save the result of the three-way merge.
The result will then be written back into the override file. There may be conflicts, which then have to be resolved manually.
After the merge operation, you will have to update your declaration to 1.1.4 in the "overrides_info.py" file.

Installation
------------

Install collective.patchwatcher by adding it to your buildout::

    [buildout]

    ...

    parts +=
        patchwatcher

    [patchwatcher]
    eggs =
        collective.patchwatcher
        ${instance:eggs}
    recipe = zc.recipe.egg
    initialization =
            import sys
            sys.argv[1:1] = "-e ${buildout:eggs-directory}".split()
    scripts = patchwatcher


and then running ``bin/buildout``. After that the script ``bin/patchwatcher`` is conveniently pre-configured with the buildout's eggs path.

Command-line options
--------------------

The command line options are the following:

::

    usage: patchwatcher [-h] [-p PACKAGES] -e EGGS_FOLDER [-w] [-dcc] [-doc]

    script for checking if there are changes

    optional arguments:
    -h, --help            show this help message and exit
    -p PACKAGES, --packages PACKAGES
                            packages list separated by commata, defaults to
                            development packages
    -e EGGS_FOLDER, --eggs-folder EGGS_FOLDER
                            eggs folder for looking up sources
    -w, --write           write the three-way merge
    -dcc, --diff-customized-current
                            show the difference in the files between your
                            customized and the current version
    -doc, --diff-old-current
                            show the difference in the files between old version
                            and the current version (needs both to be present in
                            eggs folder)

Before running patchwatcher, please ensure you have the relevant versions of the overridden packages present in your eggs folder.
Otherwise patchwatcher will complain, that it is unable to detect or apply changes.

TODO
--------

- Allow multiple eggs folders (e.g. from installations of different plone major versions) making -e an extension to the default
- Add a more comfortable way to include z3c.jbot overrides (.e.g. putting multiple override container paths into DeclarationList)
- Adjust the final statement per package (use -w if there were changes) to accomodate for the existence of changes (would need to track the changes though)
- Add a convenience parameter that creates a declarations output of suggested declarations (could be depending on override container paths)
- Group declarations by their packages (may be a breaking change)

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.patchwatcher/issues
- Source Code: https://github.com/collective/collective.patchwatcher


Support
-------

If you are having issues, please let us know via the github issue tracker or contact one of the contributors.


License
-------

The project is licensed under the GPLv2.
