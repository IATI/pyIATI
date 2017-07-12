"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.

    Implement more than Codelists.
"""
from collections import defaultdict
import os
import iati.core.codelists
import iati.core.resources


_CODELISTS = {}
"""A cache of loaded Codelists.

This removes the need to repeatedly load a Codelist from disk each time it is accessed.
"""


def codelist(name, version=None):
    """Locate the default Codelist with the specified name for the specified version of the Standard.

    Args:
        name (str): The name of the Codelist to locate.
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that the latest version of the Codelist is returned.

    Raises:
        ValueError: When a specified name is not a valid Codelist.
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        iati.core.codelists.Codelist: A Codelist with the specified name.

    Warning:
        A name may not be sufficient to act as a UID.

        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Actually handle versions, including errors.

        Better distinguish the types of ValueError.

        Better distinguish TypeErrors from KeyErrors - sometimes the latter is raised when the former should have been.
    """
    try:
        codelist_found = codelists()[name]
        return codelist_found
    except (KeyError, TypeError):
        msg = "There is no default Codelist in version {0} of the Standard with the name {1}.".format(version, name)
        iati.core.utilities.log_warning(msg)
        raise ValueError(msg)


def codelists(version=None, bypass_cache=False):
    """Locate the default Codelists for the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that the latest version of the Codelist is returned.
        bypass_cache (bool): Whether the cache should be bypassed, instead reloading data from disk even if it's already been loaded.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.core.codelists.Codelist() instances.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

        The `bypass_cache` parameter could potentially be implemented in a cleaner manner. It also shouldn't really exist until a clear use-case is defined - changes elsewhere in the library may make it redundant.

    Todo:
        Actually handle versions, including errors.

        Test a cache bypass where data is updated.

        Add a function to return a single Codelist by name.
    """
    paths = iati.core.resources.find_all_codelist_paths()

    for path in paths:
        _, filename = os.path.split(path)
        name = filename[:-len(iati.core.resources.FILE_CODELIST_EXTENSION)]  # Get the name of the codelist, without the '.xml' file extension
        if (name not in _CODELISTS.keys()) or bypass_cache:
            xml_str = iati.core.resources.load_as_string(path)
            codelist_found = iati.core.codelists.Codelist(name, xml=xml_str)
            _CODELISTS[name] = codelist_found

    return _CODELISTS


def codelist_mapping(version=None):
    """Define the mapping process which states where in a Dataset you should find values on a given Codelist.

    version (str): The version of the Standard to return the data files for. Defaults to None. This means that the mapping file is returned for the latest version of the Standard.

    Returns:
        dict of dict: A dictionary containing mapping information. Keys in the first dictionary are Codelist names. Keys in the second dictionary are `xpath` and `condition`. The condition is `None` if there is no condition.

    Todo:
        Test this.
        Stop filtering out filters for org files.

    """
    path = iati.core.resources.get_codelist_mapping_path()
    mapping_tree = iati.core.resources.load_as_tree(path)
    mappings = defaultdict(list)

    for mapping in mapping_tree.getroot().xpath('//mapping'):
        codelist_name = mapping.find('codelist').attrib['ref']
        codelist_location = mapping.find('path').text
        if 'organisation' in codelist_location:
            continue
        try:
            condition = mapping.find('condition').text
        except AttributeError:  # there is no condition
            condition = None

        mappings[codelist_name].append({
            'xpath': codelist_location,
            'condition': condition
        })

    return mappings


_SCHEMAS = {}
"""A cache of loaded Schemas.

This removes the need to repeatedly load a Schema from disk each time it is accessed.
"""


def schemas(bypass_cache=False):
    """Locate the default Schemas.

    Args:
        bypass_cache (bool): Whether the cache should be bypassed, instead reloading data from disk even if it's already been loaded.

    Returns:
        dict: A dictionary containing all the Schemas for versions of the Standard. The version of the Standard is the key. An iati.core.schemas.Schema() is each value.

    Warning:
        The `bypass_cache` parameter could potentially be implemented in a cleaner manner. It also shouldn't really exist until a clear use-case is defined - changes elsewhere in the library may make it redundant.

    Todo:
        Allow creation of Schemas by XML rather than name.

        Handle the difference between Organisation and Activity Schemas.

        Consider the Schema that defines the format of Codelists.

        Test a cache bypass where data is updated.

        Load the Schemas.
    """
    paths = iati.core.resources.find_all_schema_paths()

    for path in paths:
        name = path.split(os.sep).pop()[:-len(iati.core.resources.FILE_SCHEMA_EXTENSION)]
        if (name not in _SCHEMAS.keys()) or bypass_cache:
            schema = iati.core.schemas.Schema(name)
            _SCHEMAS[name] = schema

    return _SCHEMAS
