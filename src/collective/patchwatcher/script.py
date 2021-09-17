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
            ok &= declaration.check(logger, options.eggs_folder, options.merge)

        if ok:
            logger.info(
                "No changes detected or were applied automatically. The declarations for package {} are ready to be updated to version {}".format(
                    package, distribution.version
                )
            )
        else:
            logger.warn(
                "The package {} needs further inspection, before it's ready for version {}.".format(
                    package, distribution.version
                )
            )


if __name__ == "__main__":
    run()