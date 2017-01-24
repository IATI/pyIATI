import os
import pkg_resources

package = __name__

base_path = 'resources'
base_path_codelists = os.sep.join((base_path, 'codelists'))
base_path_codelists_non_embedded = os.sep.join((base_path_codelists, 'non_embedded'))
base_path_schemas = os.sep.join((base_path, 'schemas'))
base_path_schemas_202 = os.sep.join((base_path_schemas, '202'))


def path_codelist(name):
    """Fetch the path of a codelist with the given name

    TODO: Handle non-embedded codelists
    """
    return os.sep.join((base_path_codelists_non_embedded, '{0}.xml'.format(name)))


def path_schema(name):
    """Fetch the path of a schema with the given name

    TODO: Handle non-202 versions
    """
    return os.sep.join((base_path_schemas_202, '{0}.xsd'.format(name)))


def load_as_string(path):
    """Load a resource at the specified path into a string"""
    return pkg_resources.resource_string(package, path)
