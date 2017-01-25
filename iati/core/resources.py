"""
A module to provide a way of locating resources within the IATI library.
"""

import os
import pkg_resources

PACKAGE = __name__

BASE_PATH = 'resources'
BASE_PATH_CODELISTS = os.sep.join((BASE_PATH, 'codelists'))
BASE_PATH_CODELISTS_NON_EMBEDDED = os.sep.join((BASE_PATH_CODELISTS, 'non_embedded'))
BASE_PATH_SCHEMAS = os.sep.join((BASE_PATH, 'schemas'))
BASE_PATH_SCHEMAS_202 = os.sep.join((BASE_PATH_SCHEMAS, '202'))


def path_codelist(name):
    """Fetch the path of a codelist with the given name

    TODO: Handle non-embedded codelists
    """
    return os.sep.join((BASE_PATH_CODELISTS_NON_EMBEDDED, '{0}.xml'.format(name)))


def path_schema(name):
    """Fetch the path of a schema with the given name

    TODO: Handle non-202 versions
    """
    return os.sep.join((BASE_PATH_SCHEMAS_202, '{0}.xsd'.format(name)))


def load_as_string(path):
    """Load a resource at the specified path into a string"""
    return pkg_resources.resource_string(PACKAGE, path)
