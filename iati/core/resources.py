"""A module to provide a way of locating resources within the IATI library."""
import os
import pkg_resources
from lxml import etree


PACKAGE = __name__


BASE_PATH = 'resources'
BASE_PATH_CODELISTS = os.sep.join((BASE_PATH, 'codelists'))
BASE_PATH_CODELISTS_NON_EMBEDDED = os.sep.join((BASE_PATH_CODELISTS, 'non_embedded'))
BASE_PATH_SCHEMAS = os.sep.join((BASE_PATH, 'schemas'))
BASE_PATH_SCHEMAS_202 = os.sep.join((BASE_PATH_SCHEMAS, '202'))


def path_codelist(name):
    """Fetch the path of a codelist with the given name"""
    # TODO: Handle non-embedded codelists
    return os.sep.join((BASE_PATH_CODELISTS_NON_EMBEDDED, '{0}.xml'.format(name)))


def path_schema(name):
    """Fetch the path of a schema with the given name"""
    # TODO: Handle non-202 versions
    return os.sep.join((BASE_PATH_SCHEMAS_202, '{0}.xsd'.format(name)))


def load_as_schema(name):
    """Load a schema with the specified name into an XMLSchema"""
    path = path_schema(name)

    doc = load_as_tree(path)
    if doc:
        # TODO: surround schema conversion with error handling
        return etree.XMLSchema(doc)
    else:
        return None


def load_as_string(path):
    """Load a resource at the specified path into a string"""
    return pkg_resources.resource_string(PACKAGE, path)


def load_as_tree(path):
    """Load a schema with the specified name into an XMLSchema"""
    path_filename = resource_filename(path)
    try:
        doc = etree.parse(path_filename)
        return doc
    except OSError:
        return None


def resource_filename(path):
    """Find the file system path for a specified resource path"""
    return pkg_resources.resource_filename(PACKAGE, path)
