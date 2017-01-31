"""A module to provide a way of locating resources within the IATI library."""
import os
import pkg_resources
from lxml import etree


PACKAGE = __name__
"""The name of the resources package.

Used to locate resources when the package is distributed in certain ways that do not provide a standard filesystem.
"""

BASE_PATH = 'resources'
"""The relative location of the resources folder."""
BASE_PATH_CODELISTS = os.sep.join((BASE_PATH, 'codelists'))
"""The relative location of the folder containing codelists from the SSOT."""
BASE_PATH_CODELISTS_NON_EMBEDDED = os.sep.join((BASE_PATH_CODELISTS, 'non_embedded'))
"""The relative location of the folder containing non-embedded codelists from the SSOT."""
BASE_PATH_SCHEMAS = os.sep.join((BASE_PATH, 'schemas'))
"""The relative location of the folder containing schemas from the SSOT."""
BASE_PATH_SCHEMAS_202 = os.sep.join((BASE_PATH_SCHEMAS, '202'))
"""The relative location of the folder containing schemas from the SSOT, version 2.02 of the IATI standard."""


def path_codelist(name):
    """Determine the path of a codelist with the given name.

    Args:
        name (str): The name of the codelist to locate.

    Returns:
        str: The path to a file containing the specified codelist.

    Note:
        Does not check whether the specified codelist actually exists.

    Todo:
        Handle embedded codelists.
    """
    return os.sep.join((BASE_PATH_CODELISTS_NON_EMBEDDED, '{0}.xml'.format(name)))


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
