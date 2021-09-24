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


def run():
    arg_parser = argparse.ArgumentParser(description="script for checking if there are changes")
    arg_parser.add_argument("-p", "--packages", required=True, help="packages list")
    arg_parser.add_argument("-e", "--eggs-folder", required=True, help="eggs folder for looking up sources")
    arg_parser.add_argument("-m", "--merge", help="apply the three-way merge", action="store_true")
    options = arg_parser.parse_args(sys.argv[1:])
    packages = [package.strip() for package in options.packages.split(",")]

    all_ok = True

    for package in packages:
        distribution = get_distribution(package)
        if not distribution:
            logger.debug('Package "{}" not found.'.format(package))
            continue
        try:
            override_info = import_module(".overrides_info", package)
            declarations = getattr(override_info, "declarations")
        except ImportError, AttributeError:
            logger.debug("Could not import {}.overrides_info.declarations".format(package))
            continue

        ok = True

        for declaration in declarations:
            check = declaration.check(logger, options.eggs_folder, options.merge)
            ok &= check
        if ok:
            if options.merge:
                logger.info("No conflicts detected for all declarations of package {}.".format(package))
                # Print the chosen versions conveniently
                print(
                    "-" * 120 + "\nYou may add the following constraints to \"install_requires\" parameter in setup.py from {package}:\n\n{requirements}".format(
                        requirements="\n".join([declaration.package + "=" + str(declaration.version)]),
                        package=declaration.local_package
                    )
                )
            else:
                logger.info("No conflicts detected for all declarations of package {}. You may use -m for merging, when there were changes.".format(package))

        else:
            logger.warn("The package {} needs further inspection.".format(package))

        all_ok &= all_ok

    sys.exit(int(all_ok))


if __name__ == "__main__":
    run()