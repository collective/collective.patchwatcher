# -*- coding: utf-8 -*-
"""Init and utils."""
import glob
import os
import pkg_resources
import subprocess


class Declaration:
    """Declaration of an overridden file."""

    def __init__(self, package, version, path, local_package, local_path):
        """A declaration of an overridden file.

        :param package: package of the vanilla file
        :type package: str
        :param version: version at the time of the override
        :type version: str
        :param path: relative path within the package of the overridden file
        :type path: str
        :param local_package: own package where the overridden file lives
        :type local_package: str
        :param local_path: relative path within the own package
        :type local_path: str
        :raises FileExistsError: Thrown when the to-be overridden file could not be found.
        """
        self.package = package
        self.version = pkg_resources.parse_version(version)
        self.path = path
        self.local_path = local_path
        self.local_package = local_package
        self.distribution = pkg_resources.get_distribution(package)

        self.current_file_path = os.path.normpath(pkg_resources.resource_filename(self.distribution.project_name, path))
        self.local_file_path = os.path.normpath(pkg_resources.resource_filename(local_package, local_path))

        if not pkg_resources.resource_exists(self.distribution.project_name, path):
            raise FileExistsError("File to be overridden is not found: {}".format(self.current_file_path))

    def is_latest(self):
        """Checks if the latest version is reached.

        :return:
        :rtype: boolean
        """
        return self.distribution.parsed_version == self.version

    def get_diff(self, path_original, path_changed):
        """Perform a diff between two files. This is done by calling `diff`.

        :param path_original: path of original file
        :type path_original: str
        :param path_changed: path of changed file
        :type path_changed: str
        :return: tuple of diff's output and return code
        :rtype: tuple
        """
        path_original = os.path.normpath(path_original)
        path_changed = os.path.normpath(path_changed)

        try:
            p = subprocess.Popen(
                [
                    "diff",
                    "-p",
                    path_original,
                    path_changed,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            diff_output, _err = p.communicate()
            rc = p.returncode
        except Exception as e:
            diff_output = repr(e)
            rc = 2
        return diff_output, rc

    def merge_three_way(self, myfile, oldfile, yourfile):
        """Perform a three-way merge using diff3.

        :param myfile: my file
        :type myfile: str
        :param oldfile: old file
        :type oldfile: str
        :param yourfile: your file
        :type yourfile: str
        :return: tuple of merged result and return code
        :rtype: tuple
        """
        try:
            p = subprocess.Popen(
                ["diff3", "-m", myfile, oldfile, yourfile],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            merge_result, _err = p.communicate()
            rc = p.returncode
        except Exception as e:
            merge_result = repr(e)
            rc = 2
        return merge_result, rc

    def check(self, logger, egg_folder, merge):
        """This method checks three files:

        1) the old vanilla file (found in the eggs folder)
        2) the latest vanilla file (found in the eggs folder)
        3) the overridden file which is written against 1)

        After detecting, if there happened any changes between 1) and 2),
        there will be an attempt for a three-way merge.

        The result of the merge will be written, if wished.

        :param logger: logger
        :type logger: object
        :param egg_folder: location of the egg folder
        :type egg_folder: str
        :param merge: True if the merge result should be written (with conflicts or not)
        :type merge: boolean
        :return: True, if no changes are found or changes are merged without any conflict.
        :rtype: boolean
        """
        if self.is_latest():
            return True
        logger.info(
            "The patch for {file} in package {package} is written for version {version}. Currently installed version is however {current_version}. Checking now for changes...".format(
                file=self.path,
                package=self.package,
                version=str(self.version),
                current_version=self.distribution.version,
            )
        )
        # Look out for old original version
        # egg folder
        glob_candidates = "{egg_folder}/{package}*".format(egg_folder=egg_folder, package=self.package)

        # Search for previous versions in eggs
        for candidate in glob.glob(glob_candidates):
            tokens = candidate.split("-")
            _name, version = tokens[0], tokens[1]
            if version == str(self.version):
                break
        else:
            logger.error(
                "Did not find version {version} of package {package}".format(version=self.version, package=self.package)
            )

        # Replace versions in path
        candidate = pkg_resources.resource_filename(self.distribution.project_name, "").replace(
            str(self.distribution.parsed_version), str(self.version)
        )
        previous_file_path = os.path.normpath(os.path.join(candidate, self.path))

        # check if there are changed between the original versions
        diff_output, rc = self.get_diff(path_original=previous_file_path, path_changed=self.current_file_path)

        if rc == 0:  # no changes
            logger.info("No changes found. Nothing to do!")
            return True
        elif rc == 1:  # changes
            logger.info("Found some changes!")
            # logger.info(diff_output)
        else:  # process exited with error
            logger.error("Error while performing diff!")
            logger.error(diff_output)
            return False

        merge_result, rc = self.merge_three_way(
            myfile=self.local_file_path, oldfile=previous_file_path, yourfile=self.current_file_path
        )
        if rc == 0:  # no changes
            logger.info("Three-way merge was successful!")
        if rc == 2:
            logger.error("Error while merging three-way!")
            logger.error(merge_result)
            return False
        if rc == 1:
            logger.warn("Conflicts detected! Please fix them on your own!")
        if merge:
            with open(self.local_file_path, "wb") as file:
                file.write(merge_result)
            logger.info("Changes written into {}".format(self.local_file_path))
        return True


class DeclarationCollection(list):
    """Declarations of overridden files."""

    def __init__(self, local_package):
        """Initialize declarations

        :param local_package: name of the package, where the overridden files exist
        :type local_package: str
        """
        self.local_package = local_package

    def add(self, package, version, path, local_path):
        """Method to add a declaration to the collection

        :param package: package of the vanilla file
        :type package: str
        :param version: version at the time of the override
        :type version: str
        :param path: relative path within the package of the overridden file
        :type path: str
        :param local_package: own package where the overridden file lives
        :type local_package: str
        :param local_path: relative path within the own package
        :type local_path: str
        """
        self.append(
            Declaration(
                package=package, version=version, path=path, local_package=self.local_package, local_path=local_path
            )
        )
