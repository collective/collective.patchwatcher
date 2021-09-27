# -*- coding: utf-8 -*-
"""""Script for checking changes.

Example usage: /bin/patchwatcher -e "/home/username/zinstance/eggs" -p some.addon, some.other.addon -m
"""
from importlib import import_module

import argparse
import logging
import pkg_resources
import sys


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger("collective.patchwatcher")


def get_distribution(package_name):
    try:
        return pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        return

def is_development_package(package):
    return '/src' in package.location

def run():
    arg_parser = argparse.ArgumentParser(description="script for checking if there are changes")
    arg_parser.add_argument("-p", "--packages", required=False, help="packages list, defaults to development packages")
    arg_parser.add_argument("-e", "--eggs-folder", required=True, help="eggs folder for looking up sources")
    arg_parser.add_argument("-w", "--write", help="write the three-way merge", action="store_true")
    options = arg_parser.parse_args(sys.argv[1:])

    if options.packages:
        packages = [package.strip() for package in options.packages.split(",")]
    else:
        logger.info("No packages given. Using all development packages as default.")
        packages = [package.project_name for package in pkg_resources.working_set if is_development_package(package)]

    all_ok = True

    for package in packages:
        distribution = get_distribution(package)
        if not distribution:
            logger.debug('Package "{}" not found.'.format(package))
            continue
        try:
            override_info = import_module(".overrides_info", package)
            declarations = getattr(override_info, "declarations")
        except (ImportError, AttributeError):
            logger.debug("Could not import {}.overrides_info.declarations".format(package))
            continue

        ok = True

        for declaration in declarations:
            check = declaration.check(logger, options.eggs_folder, options.write)
            ok &= check
        if ok:
            if options.write:
                logger.info("No conflicts detected for all declarations of package {}.".format(package))
            else:
                logger.info("No conflicts detected for all declarations of package {}. You may use -w for writing back the merge result, if changes were detected.".format(package))
        else:
            logger.warn("The package {} needs further inspection.".format(package))
        if options.write:
            # Print the chosen versions conveniently
            print(
                "-" * 120 + "\nYou may add the following constraints to \"install_requires\" parameter in setup.py and overrides_info.py from {package}:\n\n{requirements}".format(
                    requirements="\n".join([declaration.package + "=" + str(declaration.version)]),
                    package=declaration.local_package
                )
            )

        all_ok &= all_ok

    sys.exit(int(all_ok))


if __name__ == "__main__":
    run()