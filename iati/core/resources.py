"""A module to provide a way of locating resources within the IATI library."""
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
BASE_PATH_CODELISTS = os.sep.join((BASE_PATH, 'codelists'))
"""The relative location of the folder containing codelists from the SSOT."""
BASE_PATH_CODELISTS_EMBEDDED = os.sep.join((BASE_PATH_CODELISTS, 'embedded'))
"""The relative location of the folder containing embedded codelists from the SSOT."""
BASE_PATH_CODELISTS_NON_EMBEDDED = os.sep.join((BASE_PATH_CODELISTS, 'non_embedded'))
"""The relative location of the folder containing non-embedded codelists from the SSOT."""
BASE_PATH_SCHEMAS = os.sep.join((BASE_PATH, 'schemas'))
"""The relative location of the folder containing schemas from the SSOT."""
BASE_PATH_SCHEMAS_202 = os.sep.join((BASE_PATH_SCHEMAS, '202'))
"""The relative location of the folder containing schemas from the SSOT, version 2.02 of the IATI standard."""

PATH_CODELIST_MAPPINGS = os.sep.join((BASE_PATH_CODELISTS, 'mapping.xml'))
"""The relative location of the file containing mappings between Schema XPaths and Codelists."""


def find_all_codelist_paths(version=0):
    """Find the paths for all codelists.

    Args:
        version (float): The version of the Standard to return the Codelists for. Defaults to 0. This means that the latest version of the Codelist is returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        list: A list of paths to all of the Codelists at the specified version of the Standard.

    Todo:
        Actually handle versions.

        Provide an argument that allows the returned list to be restricted to only Embedded or only Non-Embedded Codelists.
    """
    files_embedded = pkg_resources.resource_listdir(PACKAGE, BASE_PATH_CODELISTS_EMBEDDED)
    files_non_embedded = pkg_resources.resource_listdir(PACKAGE, BASE_PATH_CODELISTS_NON_EMBEDDED)

    paths_embedded = [path_codelist(file, 'embedded') for file in files_embedded]
    paths_non_embedded = [path_codelist(file, 'non-embedded') for file in files_non_embedded]

    paths_all = [path for path in paths_embedded + paths_non_embedded if path[-4:] == '.xml']

    return paths_all


def path_codelist(name, type='non-embedded'):
    """Determine the path of a codelist with the given name.

    Args:
        name (str): The name of the codelist to locate. Should the name end in '.xml', this shall be removed to determine the name.
        type (str): The type of codelist being located. Either 'embedded' or 'non-embedded'. Defaults to 'non-embedded'.

    Returns:
        str: The path to a file containing the specified codelist.

    Note:
        Does not check whether the specified codelist actually exists.

    Raises:
        ValueError: If the specified type of Codelist is not valid.

    Todo:
        Provide a better interface for specifying whether a codelise is Embedded or Non-Embedded.
    """
    if name[-4:] == '.xml':
        name = name[:-4]

    if type == 'embedded':
        return os.sep.join((BASE_PATH_CODELISTS_EMBEDDED, '{0}.xml'.format(name)))
    elif type == 'non-embedded':
        return os.sep.join((BASE_PATH_CODELISTS_NON_EMBEDDED, '{0}.xml'.format(name)))
    else:
        msg = "The type of a Codelist must be a string equal to either 'embedded' or 'non-embedded'"
        iati.core.utilities.log_error(msg)
        raise ValueError(msg)


def path_schema(name):
    """Determine the path of a schema with the given name.

    Args:
        name (str): The name of the schema to locate.

    Returns:
        str: The path to a file containing the specified schema.

    Note:
        Does not check whether the specified schema actually exists.

    Todo:
        Handle versions of the standard other than 2.02.
    """
    return os.sep.join((BASE_PATH_SCHEMAS_202, '{0}.xsd'.format(name)))


def load_as_string(path):
    """Load a resource at the specified path into a string.

    Args:
        path (str): The path to the file that is to be read in.

    Returns:
        str: The contents of the file at the specified location.

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
    """
    return pkg_resources.resource_filename(PACKAGE, path)
