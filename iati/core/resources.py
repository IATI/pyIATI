"""A module to provide a way of locating resources within the IATI library.

`pkg_resources` is used to allow resources to be located however the package is distributed. If using the standard `os` functionality, resources may not be locatable if, for example, the package is distributed as an egg.

Warning:
    The contents of this module are likely to change. This is due to them expecting that there is a single version of the Standard. When this assumption changes, so will the contents of this module.

    Many of the constants in this module should be deemed private to the IATI library.

    The location of SSOT content may change. It may also require network access to perform certain tasks.

Todo:
    Determine how to distribute SSOT content - with package, or separately (being downloaded at runtime)
"""
import os
import pkg_resources
from lxml import etree
import iati.core.utilities


PACKAGE = __name__
"""The name of the resources package.

Used to locate resources when the package is distributed in certain ways that do not provide a standard filesystem.
"""

BASE_PATH = 'resources'
"""The relative location of the resources folder."""
BASE_PATH_202 = os.sep.join((BASE_PATH, '202'))
"""The relative location of the resources folder for version 2.02 of the IATI Standard."""
PATH_CODELISTS = 'codelists'
"""The location of the folder containing codelists from the SSOT."""
PATH_CODELISTS_EMBEDDED = os.sep.join((PATH_CODELISTS, 'embedded'))
"""The location of the folder containing embedded codelists from the SSOT."""
PATH_CODELISTS_NON_EMBEDDED = os.sep.join((PATH_CODELISTS, 'non_embedded'))
"""The location of the folder containing non-embedded codelists from the SSOT.

Todo:
    Utilise symlinks for locating the folder for non-embedded Codelists.
"""
PATH_DATA = os.sep.join((BASE_PATH, 'data'))
"""The relative location of the folder containing IATI data files."""
PATH_SCHEMAS = 'schemas'
"""The location of the folder containing schemas from the SSOT."""
PATH_SCHEMAS_202 = os.sep.join((BASE_PATH_202, PATH_SCHEMAS))
"""The relative location of the folder containing schemas from the SSOT, version 2.02 of the IATI standard."""

FILE_CODELIST_EXTENSION = '.xml'
"""The extension of a file containing a Codelist."""

FILE_DATA_EXTENSION = '.xml'
"""The extension of a file containing IATI data."""

FILE_SCHEMA_ACTIVITY_NAME = 'iati-activities-schema'
"""The name of a file containing an Activity Schema."""
FILE_SCHEMA_ORGANISATION_NAME = 'iati-organisations-schema'
"""The name of a file containing an Organisation Schema."""
FILE_SCHEMA_EXTENSION = '.xsd'
"""The extension of a file containing a Schema."""


def find_all_codelist_paths(version=None):
    """Find the paths for all codelists.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that paths to the latest version of the Codelists are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the Codelists at the specified version of the Standard.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Handle versions, including errors.

        Provide an argument that allows the returned list to be restricted to only Embedded or only Non-Embedded Codelists.
    """
    files_embedded = pkg_resources.resource_listdir(PACKAGE, path_for_version(PATH_CODELISTS_EMBEDDED, version))
    files_non_embedded = pkg_resources.resource_listdir(PACKAGE, path_for_version(PATH_CODELISTS_NON_EMBEDDED, version))

    paths_embedded = [path_codelist(file, 'embedded', version) for file in files_embedded]
    paths_non_embedded = [path_codelist(file, 'non-embedded', version) for file in files_non_embedded]

    paths_all = [path for path in paths_embedded + paths_non_embedded if path[-4:] == FILE_CODELIST_EXTENSION]

    return paths_all


def find_all_schema_paths(version=None):
    """Find the paths for all schemas.

    Args:
        version (str): The version of the Standard to return the Schemas for. Defaults to None. This means that paths to the latest version of the Schemas are returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the Schemas at the specified version of the Standard.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Handle versions, including errors.

        Implement for more than a single specified activity schema.
    """
    return [path_schema(FILE_SCHEMA_ACTIVITY_NAME, version)]


def path_codelist(name, location='non-embedded', version=0):
    """Determine the path of a codelist with the given name.

    Args:
        name (str): The name of the codelist to locate. Should the name end in '.xml', this shall be removed to determine the name.
        location (str): The location of the codelist. Either 'embedded' or 'non-embedded'. Defaults to 'non-embedded'.
        version (float): The version of the Standard to return the Schemas for. Defaults to 0. This means that the latest version of the Schema is returned.

    Returns:
        str: The path to a file containing the specified codelist.

    Note:
        Does not check whether the specified codelist actually exists.

    Raises:
        ValueError: If the specified location of Codelist is not valid.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

        Use of magic strings in the `location` parameter is not a tidy interface.

        It needs to be determined how best to locate a user-defined Codelist that is available at a URL that needs fetching.

    Todo:
        Provide a better interface for specifying whether a codelist is Embedded or Non-Embedded, keeping in mind user-defined codelists.

        Test this.
    """
    if name[-4:] == FILE_CODELIST_EXTENSION:
        name = name[:-4]

    if location == 'embedded':
        return path_for_version(os.sep.join((PATH_CODELISTS_EMBEDDED, '{0}'.format(name) + FILE_CODELIST_EXTENSION)), version)
    elif location == 'non-embedded':
        return path_for_version(os.sep.join((PATH_CODELISTS_NON_EMBEDDED, '{0}'.format(name) + FILE_CODELIST_EXTENSION)), version)
    else:
        msg = "The location of a Codelist must be a string equal to either 'embedded' or 'non-embedded'"
        iati.core.utilities.log_error(msg)
        raise ValueError(msg)


def path_data(name):
    """Determine the path of an IATI data file with the given name.

    Args:
        name (str): The name of the data file to locate.
        version (float): The version of the Standard to return the Schemas for. Defaults to 0. This means that the latest version of the Schema is returned.

    Returns:
        str: The path to a file containing the specified data.

    Note:
        Does not check whether the specified data file actually exists.

    Warning:
        Needs to handle a more complex file structure than a single flat directory.

    Todo:
        Test this.
    """
    return os.sep.join((PATH_DATA, '{0}'.format(name) + FILE_DATA_EXTENSION))


def path_schema(name, version=0):
    """Determine the path of a schema with the given name.

    Args:
        name (str): The name of the schema to locate.
        version (float): The version of the Standard to return the Schemas for. Defaults to 0. This means that the latest version of the Schema is returned.

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
    return path_for_version(os.sep.join((PATH_SCHEMAS, '{0}'.format(name) + FILE_SCHEMA_EXTENSION)), version)


def path_for_version(path, version=0):
    """Determine the relative location of a specified path at the specified version of the IATI Standard.

    Args:
        path (str): The path to the file that is to be read in.
        version (float): The version of the IATI Standard to locate data for.

    Returns:
        str: The relative path to a file at the specified version of the standard.

    Note:
        Does not check whether anything exists at the specified path.

    Todo:
        Handle versions of the standard other than 2.02.

        Test this.
    """
    return os.sep.join((BASE_PATH_202, path))


def load_as_string(path):
    """Load a resource at the specified path into a string.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        str: The contents of the file at the specified location.

    Warning:
        Should raise Exceptions when there are problems loading the requested data.

    Todo:
        Add error handling for when the specified file does not exist.
    """
    return pkg_resources.resource_string(PACKAGE, path)


def load_as_tree(path):
    """Load a schema with the specified name into an ElementTree.

    Args:
        path (str): The path to the file that is to be converted to an ElementTree.
            The file at the specified location must contain valid XML.

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
