"""A module to provide a way of locating resources within the IATI library.

The `get_*_path[s](name)` functions provide information about where to locate particular types of resources with a provided name.

Warning:
    Many of the constants in this module should be deemed private to the IATI library.

    The location of SSOT content may change. It may also require network access to perform certain tasks.

Todo:
    Determine how to distribute SSOT content - with package, or separately (being downloaded at runtime).

"""
import os
import pkg_resources
import iati.constants
import iati.utilities


PACKAGE = __name__
"""The name of the resources package.

Used to locate resources when the package is distributed in certain ways that do not provide a standard filesystem.

"""

BASE_PATH = 'resources'
"""The relative location of the resources folder."""
BASE_PATH_STANDARD = os.path.join(BASE_PATH, 'standard')
"""The relative location of resources related to the IATI Standard."""
BASE_PATH_LIB_DATA = os.path.join(BASE_PATH, 'lib_data')
"""The relative location of resources not related to the IATI Standard."""
PATH_CODELISTS = 'codelists'
"""The location of the folder containing Codelists from the SSOT."""
PATH_SCHEMAS = 'schemas'
"""The location of the folder containing Schemas from the SSOT."""
PATH_RULESETS = 'rulesets'
"""The location of the folder containing Rulesets from the SSOT."""

FILE_CODELIST_EXTENSION = '.xml'
"""The expected extension of a file containing a Codelist."""
FILE_CODELIST_MAPPING = 'codelist-mapping.xml'
"""The name of a file containing definitions of how Codelist values map to data."""
FILE_DATA_EXTENSION = '.xml'
"""The expected extension of a file containing IATI data."""
FILE_RULESET_EXTENSION = '.json'
"""The expected extension of a file containing a Ruleset."""
FILE_SCHEMA_EXTENSION = '.xsd'
"""The expected extension of a file containing a Schema."""

FILE_RULESET_SCHEMA_NAME = 'ruleset_schema'
"""The name of a file containing the Ruleset schema."""
FILE_RULESET_STANDARD_NAME = 'standard_ruleset'
"""The name of a file containing the Standard Ruleset."""
FILE_SCHEMA_ACTIVITY_NAME = 'iati-activities-schema'
"""The name of a file containing an Activity Schema."""
FILE_SCHEMA_ORGANISATION_NAME = 'iati-organisations-schema'
"""The name of a file containing an Organisation Schema."""


def get_codelist_paths(version=None):
    """Find the paths for all Codelists at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that paths to a version-independent version of the Codelists are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Codelists at the specified version of the Standard.

    Todo:
        Further exploration needs to be undertaken in how to handle pre-1.04 versions of the Standard.

        Add tests to show that versions 1.04 and above are being correctly handled, including errors.

        Provide an argument that allows the returned list to be restricted to only Embedded or only Non-Embedded Codelists.

    """
    folder_path = path_for_version(PATH_CODELISTS, version)
    files = pkg_resources.resource_listdir(PACKAGE, folder_path[len(resource_filesystem_path('')):])
    files_codelists_only = [file_name for file_name in files if file_name[-4:] == FILE_CODELIST_EXTENSION]
    paths = [create_codelist_path(file_name, version) for file_name in files_codelists_only]

    return paths


def get_codelist_mapping_paths(version=None):
    """Find the paths for all Codelist Mapping files at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Codelist Mapping file for. Defaults to None. This means that paths to the latest version of the Codelist Mapping file are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Codelist Mapping files at the specified version of the Standard.

    Todo:
        Further exploration needs to be undertaken in how to handle pre-1.04 versions of the Standard.

        Add tests to show that versions 1.04 and above are being correctly handled, including errors.

    """
    paths = [create_codelist_mapping_path(version)]

    return paths


def get_ruleset_paths(version=None):
    """Find the paths for all Rulesets at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Rulesets for. Defaults to None. This means that paths to the latest version of the Rulesets are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Rulesets at the specified version of the Standard.

    Todo:
        Further exploration needs to be undertaken in how to handle pre-1.04 versions of the Standard.

        Add tests to show that versions 1.04 and above are being correctly handled, including errors.

    """
    paths = [create_ruleset_path(FILE_RULESET_STANDARD_NAME, version)]

    return paths


def get_all_schema_paths(version=None):
    """Find the paths for all Schemas at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Schemas for. Defaults to None. This means that paths to a version-independent version of the Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Consider adding the IATI Codelist Schema.

    """
    return get_activity_schema_paths(version) + get_organisation_schema_paths(version)


def get_activity_schema_paths(version=None):
    """Find the paths for all Activity Schemas at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the activity schemas for. Defaults to None. This means that paths to a version-independent version of the Activity Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Activity Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Look to match against integers so there is a clear reason to return a list rather than a single Schema.

    """
    return [create_schema_path(FILE_SCHEMA_ACTIVITY_NAME, version)]


def get_organisation_schema_paths(version=None):  # pylint: disable=invalid-name
    """Find the paths for all Organisation Schemas at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Organisation schemas for. Defaults to None. This means that paths to a version-independent version of the Organisation Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list(str): A list of paths to all of the Organisation Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Look to match against integers so there is a clear reason to return a list rather than a single Schema.


    """
    return [create_schema_path(FILE_SCHEMA_ORGANISATION_NAME, version)]


def create_codelist_path(codelist_name, version=None):
    """Determine the path of a Codelist with the given name at the specified version of the Standard.

    Args:
        codelist_name (str): The name of the codelist to locate. Should the name end in `.xml`, this shall be removed to determine the name.
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that a path to a version-independent version of the Codelist is returned.

    Returns:
        str: The path to a file containing the specified Codelist.

    Raises:
        TypeError: When the codelist name is not a string.
        ValueError: When an invalid version is specified.

    Note:
        Does not check whether the specified Codelist actually exists.

    Warning:
        It needs to be determined how best to locate a user-defined Codelist that is available at a URL that needs fetching.

    """
    if not isinstance(codelist_name, str):
        raise TypeError('The name of a Codelist must be a string, not a {0}'.format(type(codelist_name)))

    if codelist_name[-4:] == FILE_CODELIST_EXTENSION:
        codelist_name = codelist_name[:-4]

    return path_for_version(os.path.join(PATH_CODELISTS, '{0}'.format(codelist_name) + FILE_CODELIST_EXTENSION), version)


def create_codelist_mapping_path(version=None):
    """Determine the path of the Codelist mapping file.

    version (str): The version of the Standard to return the data files for.
        Decimal: Return a path for the specified version of the Standard.
        Integer: Return a path for the latest Decimal version within the given integer.

    Raises:
        ValueError: If an invalid version is specified.

    Returns:
        str: The path to a file containing the mapping file.

    """
    try:
        if int(version) in iati.constants.STANDARD_VERSIONS_MAJOR:
            version = max(iati.utilities.versions_for_integer(version))
    except ValueError:
        pass  # a non-major version has been specified
    except (OverflowError, TypeError):
        raise ValueError('The version must be a Decimal or Integer version of the IATI Standrd, not {0}'.format(version))

    return path_for_version(FILE_CODELIST_MAPPING, version)


def create_lib_data_path(name):
    """Determine the path of a general library data file with the given name.

    The data file is not part of the IATI Standard. It is also required in the library itself, not just for testing purposes.

    Args:
        name (str): The name of the data file to locate. The name must include the file extension.

    Returns:
        str: The path to the specified file.

    Note:
        Does not check whether the specified file actually exists.

    """
    return resource_filesystem_path(os.path.join(BASE_PATH_LIB_DATA, name))


def create_ruleset_path(name, version=None):
    """Determine the path of a Ruleset with the given name at the specified version of the Standard.

    Args:
        name (str): The name of the Ruleset to locate.
        version (str): The version of the Standard to return the Ruleset for. Defaults to None. This means that paths to a version-independent version of the Ruleset are returned.

    Returns:
        str: The path to a file containing the specified ruleset.

    Note:
        Does not check whether the specified ruleset actually exists.

    Todo:
        Test this directly rather than just the indirect tests that exist at present.

    """
    return path_for_version(os.path.join(PATH_RULESETS, '{0}'.format(name) + FILE_RULESET_EXTENSION), version)


def create_schema_path(name, version=None):
    """Determine the path of a Schema with the given name at the specified version of the Standard.

    Args:
        name (str): The name of the Schema to locate.
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that paths to a version-independent version of the Schema is returned.

    Returns:
        str: The path to a file containing the specified Schema.

    Note:
        Does not check whether the specified Schema actually exists.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Test this directly rather than just the indirect tests that exist at present.

    """
    return path_for_version(os.path.join(PATH_SCHEMAS, '{0}'.format(name) + FILE_SCHEMA_EXTENSION), version)


def folder_name_for_version(version=None):
    """Return the folder name for a given version of the Standard.

    Args:
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the folder name independent of any version of the Standard is returned.

    Returns:
        str: The folder name for the specified version of the Standard.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Todo:
        Extract magic string: 'version-independent'

    """
    if version is None:
        return 'version-independent'

    if version in iati.constants.STANDARD_VERSIONS:
        return version.replace('.', '-')
    elif version in [str(major_version) for major_version in iati.constants.STANDARD_VERSIONS_MAJOR]:
        return version
    else:
        raise ValueError("Version {} is not a valid version of the IATI Standard.".format(version))


def folder_path_for_version(version=None):
    """Return the path for the folder containing SSOT data (schemas, codelists etc) at the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the path independent of any version of the Standard is returned.

    Returns:
        str: The relative path to the folder for containing SSOT data the specified version of the Standard.

    """
    return os.path.join(BASE_PATH_STANDARD, folder_name_for_version(version))


def path_for_version(path, version=None):
    """Return the relative location of a specified path at the specified version of the Standard.

    Args:
        path (str): The path to the file that is to be read in.
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the path independent of any version of the Standard is returned.

    Returns:
        str: The relative path to a file at the specified version of the Standard.

    Note:
        Does not check whether anything exists at the specified path.

    Todo:
        Test this directly rather than just the indirect tests that exist at present.

    """
    return resource_filesystem_path(os.path.join(folder_path_for_version(version), path))


def resource_filesystem_path(path):
    """Find the file system path for a specified resource path.

    Args:
        path (str): The path of the file that is to be located.

    Returns:
        str: A reference to the specified file that works however the package is distributed.

    Note:
        Does not check to see that the specified file exists.

    Warning:
        When other functions in this module are reviewed, this will be too.

    """
    return pkg_resources.resource_filename(PACKAGE, path)
