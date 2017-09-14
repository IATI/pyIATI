"""A module to provide a way of locating resources within the IATI library.

There are two key groups of functions within this module: `get_*_path[s]()` and `load_as_*()`.

The `get_*_path[s](name)` functions provide information about where to locate particular types of resources with a provided name.

The `load_as_*(path)` functions load the contents of a file at the specified path and return it in the specified format.

Example:
    To load a test XML file located in `my_test_file` and use it to create a `Dataset`::

        dataset = iati.core.Dataset(iati.core.resources.load_as_string(iati.core.resources.get_test_data_path('my_test_file')))

Note:
    `pkg_resources` is used to allow resources to be located however the package is distributed. If using the standard `os` functionality, resources may not be locatable if, for example, the package is distributed as an egg.

Warning:
    The contents of this module are likely to change. This is due to them expecting that there is a single version of the Standard. When this assumption changes, so will the contents of this module.

    Many of the constants in this module should be deemed private to the IATI library.

    The location of SSOT content may change. It may also require network access to perform certain tasks.

Todo:
    Determine how to distribute SSOT content - with package, or separately (being downloaded at runtime).

"""
import os
import pkg_resources
from lxml import etree
import iati.core.constants


PACKAGE = __name__
"""The name of the resources package.

Used to locate resources when the package is distributed in certain ways that do not provide a standard filesystem.

"""

BASE_PATH = 'resources'
"""The relative location of the resources folder."""
BASE_PATH_STANDARD = os.path.join(BASE_PATH, 'standard')
"""The relative location of resources related to the IATI Standard."""
PATH_CODELISTS = 'codelists'
"""The location of the folder containing codelists from the SSOT."""
PATH_TEST_DATA = os.path.join(BASE_PATH, 'test_data')
"""The relative location of the folder containing IATI data files."""
PATH_SCHEMAS = 'schemas'
"""The location of the folder containing schemas from the SSOT."""
PATH_RULESETS = 'rulesets'
"""The location of the folder containing rulesets from the SSOT."""

FILE_CODELIST_EXTENSION = '.xml'
"""The extension of a file containing a Codelist."""

FILE_DATA_EXTENSION = '.xml'
"""The extension of a file containing IATI data."""

FILE_RULESET_EXTENSION = '.json'
"""The extension of a file containing a Ruleset."""

FILE_RULESET_SCHEMA_NAME = 'ruleset_schema'
"""The name of a file containing the Ruleset schema."""
FILE_RULESET_STANDARD_NAME = 'standard_ruleset'
"""The name of a file containing the Standard Ruleset."""
FILE_SCHEMA_ACTIVITY_NAME = 'iati-activities-schema'
"""The name of a file containing an Activity Schema."""
FILE_SCHEMA_ORGANISATION_NAME = 'iati-organisations-schema'
"""The name of a file containing an Organisation Schema."""
FILE_SCHEMA_EXTENSION = '.xsd'
"""The extension of a file containing a Schema."""


def get_all_codelist_paths(version=None):
    """Find the paths for all codelists.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that paths to the latest version of the Codelists are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the Codelists at the specified version of the Standard.

    Todo:
        Further exploration needs to be undertaken in how to handle pre-1.04 versions of the Standard.

        Add tests to show that versions 1.04 and above are being correctly handled, including errors.

        Provide an argument that allows the returned list to be restricted to only Embedded or only Non-Embedded Codelists.

    """
    files = pkg_resources.resource_listdir(PACKAGE, get_path_for_version(PATH_CODELISTS, version))
    files_codelists_only = [file_name for file_name in files if file_name[-4:] == FILE_CODELIST_EXTENSION]
    paths = [get_codelist_path(file_name, version) for file_name in files_codelists_only]

    return paths


def get_all_schema_paths(version=None):
    """Find the paths for all schemas.

    Args:
        version (str): The version of the Standard to return the Schemas for. Defaults to None. This means that paths to the latest version of the Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Potentially add the IATI codelist schema.

    """
    return get_all_activity_schema_paths(version) + get_all_org_schema_paths(version)


def get_all_activity_schema_paths(version=None):
    """Find the paths for all activity schemas.

    Args:
        version (str): The version of the Standard to return the activity schemas for. Defaults to None. This means that paths to the latest version of the activity Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list of str: A list of paths to all of the activity Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Potentially add the IATI codelist schema.

    """
    return [get_schema_path(FILE_SCHEMA_ACTIVITY_NAME, version)]


def get_all_org_schema_paths(version=None):
    """Find the paths for all organisation schemas.

    Args:
        version (str): The version of the Standard to return the organisation schemas for. Defaults to None. This means that paths to the latest version of the activity Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the organisation Schemas at the specified version of the Standard.

    Todo:
        Add tests for version parameters that are invalid.

        Potentially add the IATI codelist schema.

    """
    return [get_schema_path(FILE_SCHEMA_ORGANISATION_NAME, version)]


def get_codelist_path(codelist_name, version=None):
    """Determine the path of a codelist with the given name.

    Args:
        codelist_name (str): The name of the codelist to locate. Should the name end in '.xml', this shall be removed to determine the name.
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that paths to the latest version of the Codelists are returned.

    Returns:
        str: The path to a file containing the specified codelist.

    Note:
        Does not check whether the specified codelist actually exists.

    Warning:
        It needs to be determined how best to locate a user-defined Codelist that is available at a URL that needs fetching.

    """
    if codelist_name[-4:] == FILE_CODELIST_EXTENSION:
        codelist_name = codelist_name[:-4]

    return get_path_for_version(os.path.join(PATH_CODELISTS, '{0}'.format(codelist_name) + FILE_CODELIST_EXTENSION), version)


def get_test_data_path(name, version=None):
    """Determine the path of an IATI data file with the given filename.

    Args:
        name (str): The name of the data file to locate. The filename must not contain the '.xml' file extension.
        version (float): The version of the Standard to return the data files for. Defaults to None. This means that the path is returned for a filename at the latest version of the Standard.

    Returns:
        str: The path to a file containing the specified data.

    Note:
        Does not check whether the specified data file actually exists.

    Warning:
        Needs to handle a more complex file structure than a single flat directory.

    Todo:
        Test this.

    """
    return os.path.join(PATH_TEST_DATA, get_folder_name_for_version(version), '{0}'.format(name) + FILE_DATA_EXTENSION)


def get_test_ruleset_path(name, version=None):
    """Determine the path of an IATI test Ruleset file with the given filename.

    Args:
        name (str): The name of the data file to locate. The filename must not contain the '.json' file extension.
        version (float): The version of the Standard to return the data files for. Defaults to None. This means that the path is returned for a filename at the latest version of the Standard.

    Returns:
        str: The path to a file containing the specified test Ruleset.

    Note:
        Does not check whether the specified file actually exists.

    Warning:
        Needs to handle a more complex file structure than a single flat directory.

    Todo:
        Might need removing. What is using it now?

    """
    return os.path.join(PATH_TEST_DATA, get_folder_name_for_version(version), 'rulesets/{0}'.format(name) + FILE_RULESET_EXTENSION)


def get_folder_name_for_version(version=None):
    """Return the folder name for a given version of the Standard.

    Args:
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the folder name corresponding to the latest version of the Standard is returned.

    Returns:
        str: The folder name for the specified version of the Standard.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    """
    if version is None:
        version = iati.core.constants.STANDARD_VERSION_LATEST

    if version in iati.core.constants.STANDARD_VERSIONS:
        return version.replace('.', '')
    else:
        raise ValueError("Version {} is not a valid version of the IATI Standard.".format(version))


def get_ruleset_path(name, version=None):
    """Determine the path of a ruleset with the given name.

    Args:
        name (str): The name of the ruleset to locate.
        version (str): The version of the Standard to return the Ruleset for. Defaults to None. This means that paths to the latest version of the Ruleset are returned.

    Returns:
        str: The path to a file containing the specified ruleset.

    Note:
        Does not check whether the specified ruleset actually exists.

    Todo:
        Test this.

    """
    return get_path_for_version(os.path.join(PATH_RULESETS, '{0}'.format(name) + FILE_RULESET_EXTENSION), version)


def get_schema_path(name, version=None):
    """Determine the path of a schema with the given name.

    Args:
        name (str): The name of the schema to locate.
        version (str): The version of the Standard to return the Schemas for. Defaults to None. This means that paths to the latest version of the Schemas are returned.

    Returns:
        str: The path to a file containing the specified schema.

    Note:
        Does not check whether the specified schema actually exists.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Handle versions of the standard other than 2.02.

        Test this.

    """
    return get_path_for_version(os.path.join(PATH_SCHEMAS, '{0}'.format(name) + FILE_SCHEMA_EXTENSION), version)


def get_folder_path_for_version(version=None):
    """Return the path for the folder containing SSOT data (schemas, codelists etc) for a given version of the Standard.

    Args:
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the path corresponding to the latest version of the Standard is returned.

    Returns:
        str: The relative path to the folder for containing SSOT data the specified version of the Standard.

    """
    return os.path.join(BASE_PATH_STANDARD, get_folder_name_for_version(version))


def get_path_for_version(path, version=None):
    """Return the relative location of a specified path at the specified version of the IATI Standard.

    Args:
        path (str): The path to the file that is to be read in.
        version (str): The version of the Standard to return the folder path for. Defaults to None. This means that the path corresponding to the latest version of the Standard is returned.

    Returns:
        str: The relative path to a file at the specified version of the Standard.

    Note:
        Does not check whether anything exists at the specified path.

    Todo:
        Test this.

    """
    return os.path.join(get_folder_path_for_version(version), path)


def load_as_bytes(path):
    """Load a resource at the specified path into a bytes object.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        bytes: The contents of the file at the specified location.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.

    Todo:
        Ensure all reasonably possible OSErrors are documented here and in functions that call this.
        Add error handling for when the specified file does not exist.
        Pass in PACKAGE as a default parameter, so that this code can be used by other library modules (e.g. iati.fetch).

    """
    return pkg_resources.resource_string(PACKAGE, path)


def load_as_dataset(path):
    """Load a resource at the specified path into a dataset.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        dataset: A Dataset object with the contents of the file at the specified location.

    Warning:
        Should raise Exceptions when there are problems loading the requested data.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.
        ValueError: When a file at the specified path does not contain valid XML.

    Todo:
        Add error handling for when the specified file does not exist.

    """
    dataset_str = load_as_string(path)

    return iati.core.Dataset(dataset_str)


def load_as_string(path):
    """Load a resource at the specified path into a string.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        str (python3) / unicode (python2): The contents of the file at the specified location.

    Raises:
        FileNotFoundError (python3) / IOError (python2): When a file at the specified path does not exist.

    Todo:
        Pass in PACKAGE as a default parameter, so that this code can be used by other library modules (e.g. iati.fetch).

    """
    return load_as_bytes(path).decode('utf-8')


def load_as_tree(path):
    """Load a schema with the specified name into an ElementTree.

    Args:
        path (str): The path to the file that is to be converted to an ElementTree. The file at the specified location must contain valid XML.

    Returns:
        etree._ElementTree: An ElementTree representing the parsed XML.

    Raises:
        OSError: An error occurred accessing the specified file.

    Warning:
        There should be errors raised when the request is to load something that is not valid XML.
        Does not fully hide the lxml internal workings. This includes making reference to a private lxml type.

    Todo:
        Handle when the specified file can be accessed without issue, but it does not contain valid XML.

    """
    path_filename = resource_filename(path)
    try:
        doc = etree.parse(path_filename)
        return doc
    except OSError:
        raise


def resource_filename(path):
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
