# -*- coding: utf-8 -*-
"""""Script for checking changes.

Example usage: /bin/patchwatcher -e "/home/username/zinstance/eggs" -p some.addon, some.other.addon -m
"""
from importlib import import_module

import argparse
import logging
import pkg_resources
import sys


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format="%(message)s")
logger = logging.getLogger("collective.patchwatcher")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_distribution(package_name):
    try:
        return pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        return


def is_development_package(package):
    # XXX: There is probably a saner way to determine development packages
    return "/src/" in package.location


def run():
    arg_parser = argparse.ArgumentParser(
        description="script for checking if there are changes"
    )
    arg_parser.add_argument(
        "-p",
        "--packages",
        required=False,
        help="packages list separated by commata, defaults to development packages",
    )
    arg_parser.add_argument(
        "-e", "--eggs-folder", required=True, help="eggs folder for looking up sources"
    )
    arg_parser.add_argument(
        "-w", "--write", help="write the three-way merge", action="store_true"
    )
    arg_parser.add_argument(
        "-dcc",
        "--diff-customized-current",
        help="show the difference in the files between your customized and the current version",
        action="store_true",
    )
    arg_parser.add_argument(
        "-doc",
        "--diff-old-current",
        help="show the difference in the files between old version and the current version (needs both to be present in eggs folder)",
        action="store_true",
    )
    options = arg_parser.parse_args(sys.argv[1:])

    diff_options = {
        k.replace("diff_", ""): v
        for (k, v) in vars(options).items()
        if k.startswith("diff_")
    }
    if options.packages:
        packages = [package.strip() for package in options.packages.split(",")]
    else:
        logger.info("No packages given. Using all development packages as default.")
        packages = [
            package.project_name
            for package in pkg_resources.working_set
            if is_development_package(package)
        ]

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
            logger.debug(
                "Could not import {}.overrides_info.declarations".format(package)
            )
            continue

        ok = True

        for declaration in declarations:
            check = declaration.check(
                logger, options.eggs_folder, options.write, diff_options
            )
            ok &= check
        if ok:
            if options.write:
                logger.info(
                    "No conflicts detected for all declarations of package {}.".format(
                        package
                    )
                )
            else:
                logger.info(
                    "No conflicts detected for all declarations of package {}. You may use -w for writing back the merge result, if changes were detected.".format(
                        package
                    )
                )
        else:
            logger.warn("The package {} needs further inspection.".format(package))
        if options.write or True:
            summary_packages = sorted(set([(declaration.package, str(declaration.distribution.version)) for declaration in declarations]))
            # Print the chosen versions conveniently
            print(
                "-" * 120
                + '\nYou may add the following constraints to "install_requires" parameter in setup.py and the declarations in overrides_info.py of your packages:\n{requirements}'.format(
                    requirements="\n".join(
                        [
                            package
                            + "="
                            + version
                            for (package, version) in summary_packages
                        ]
                    ),
                )
                + "\n"
                + "-" * 120
            )

        all_ok &= all_ok

    sys.exit(int(all_ok))


if __name__ == "__main__":
    run()
