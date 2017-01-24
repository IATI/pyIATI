import os
import pkg_resources

package = __name__

base_path = 'resources'
base_path_codelists = os.sep.join((base_path, 'codelists'))
base_path_codelists_non_embedded = os.sep.join((base_path_codelists, 'non_embedded'))
flow_type_path = os.sep.join(('resources', 'codelists', 'non_embedded', 'FlowType.xml'))


def path_codelist(name):
    """Fetch the path of a codelist with the given name

    TODO: Handle non-embedded codelists
    """
    return os.sep.join((base_path_codelists_non_embedded, '{0}.xml'.format(name)))


def load_as_string(path):
    """Load a resource at the specified path into a string"""
    return pkg_resources.resource_string(package, path)
