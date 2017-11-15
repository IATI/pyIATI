"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.
    Implement more than Codelists.
"""

import json
import os
from collections import defaultdict
from copy import deepcopy
import iati.codelists
import iati.constants
import iati.resources


def _specific_version_for(version):
    """Convert a version number into the most appropriate Decimal Version.

    * Decimal Versions will remain unchanged.
    * Integer Versions will return the latest Decimal Version within the Integer.

    Args:
        version (str): The version to obtain a specific version for.

    Raises:
        ValueError: When a specified version cannot be converted to a valid version of the IATI Standard.

    Returns:
        str: The Decimal Version of the Standard that the input version relates to.

    """
    if version in iati.constants.STANDARD_VERSIONS:
        return version
    elif version in [str(v) for v in iati.constants.STANDARD_VERSIONS_MAJOR]:
        decimals_for_integer = [v for v in iati.constants.STANDARD_VERSIONS if v[0] == version]
        return max(decimals_for_integer)
    else:
        raise ValueError('Version {0} is not a valid version of the IATI Standard.'.format(version))


_CODELISTS = defaultdict(dict)
"""A cache of loaded Codelists.

This removes the need to repeatedly load a Codelist from disk each time it is accessed.

The dictionary is structured as:

{
    "version_number_a": {
        "codelist_name_1": iati.Codelist(codelist_1),
        "codelist_name_2": iati.Codelist(codelist_2)
        [...]
    },
    "version_number_b": {
        [...]
    },
    [...]
}

Warning:
    Modifying values directly obtained from this cache can potentially cause unexpected behavior. As such, it is highly recommended to perform a `deepcopy()` on any accessed Codelist before it is modified in any way.

"""


def codelist(name, version):
    """Return the default Codelist with the specified name for the specified version of the Standard.

    Args:
        name (str): The name of the Codelist to return.
        version (str): The Integer or Decimal version of the Standard to return the Codelist for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.

    Raises:
        ValueError: When a specified name is not a Codelist at the specified version of the Standard.
        ValueError: When a specified version is not a valid version of the Standard.

    Returns:
        iati.Codelist: A Codelist with the specified name from the specified version of the Standard. It is populated with all the Codes on the Codelist.

    Warning:
        A name may not be sufficient to act as a UID.

        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

    Todo:
        Better distinguish the types of ValueError.

        Better distinguish TypeErrors from KeyErrors - sometimes the latter is raised when the former should have been.

        Determine how to handle requested an Embedded Codelist for an Integer Version.

    """
    try:
        codelist_found = _codelists(version, True)[name]
        return deepcopy(codelist_found)
    except (KeyError, TypeError):
        msg = "There is no default Codelist in version {0} of the Standard with the name {1}.".format(version, name)
        iati.utilities.log_warning(msg)
        raise ValueError(msg)


def _codelists(version, use_cache=False):
    """Locate the default Codelists for the specified version of the Standard.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Codelists for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.
        use_cache (bool): Whether the cache should be used rather than loading the Codelists from disk again. If used, a `deepcopy()` should be performed on any returned Codelist before it is modified.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.Codelist() instances.

    Warning:
        Setting `use_cache` to `True` is dangerous since it does not return a deep copy of the Codelists. This means that modification of a returned Codelist will modify the Codelist everywhere.
        A `deepcopy()` should be performed on any returned value before it is modified.

    Note:
        This is a private function so as to prevent the (dangerous) `use_cache` parameter being part of the public API.

    """
    version = _specific_version_for(version)

    paths = iati.resources.get_all_codelist_paths(version)

    for path in paths:
        _, filename = os.path.split(path)
        name = filename[:-len(iati.resources.FILE_CODELIST_EXTENSION)]  # Get the name of the codelist, without the '.xml' file extension
        if (name not in _CODELISTS[version].keys()) or not use_cache:
            xml_str = iati.utilities.load_as_string(path)
            codelist_found = iati.Codelist(name, xml=xml_str)
            _CODELISTS[version][name] = codelist_found

    return _CODELISTS[version]


def codelists(version):
    """Return the default Codelists for the specified version of the Standard.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Codelists for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.Codelist() instances, populated with the relevant Codes.

    """
    return _codelists(version)


def codelist_mapping(version):
    """Define the mapping process which states where in a Dataset you should find values on a given Codelist.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Codelist Mapping File for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict of dict: A dictionary containing mapping information. Keys in the first dictionary are Codelist names. Keys in the second dictionary are `xpath` and `condition`. The condition is `None` if there is no condition.

    Todo:
        Make use of the `version` parameter.

    """
    version = _specific_version_for(version)

    path = iati.resources.get_codelist_mapping_path(version)
    mapping_tree = iati.utilities.load_as_tree(path)
    mappings = defaultdict(list)

    for mapping in mapping_tree.getroot().xpath('//mapping'):
        codelist_name = mapping.find('codelist').attrib['ref']
        codelist_location = mapping.find('path').text

        try:
            condition = mapping.find('condition').text
        except AttributeError:  # there is no condition
            condition = None

        mappings[codelist_name].append({
            'xpath': codelist_location,
            'condition': condition
        })

    return mappings


def ruleset(version):
    """Return the Standard Ruleset for the specified version of the Standard.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Standard Ruleset for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        iati.Ruleset: The default Ruleset for the specified version of the Standard.

    """
    version = _specific_version_for(version)

    path = iati.resources.get_ruleset_path(iati.resources.FILE_RULESET_STANDARD_NAME, version)
    ruleset_str = iati.utilities.load_as_string(path)

    return iati.Ruleset(ruleset_str)


def ruleset_schema():
    """Return the Ruleset schema for the specified version of the Standard.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary representing the Ruleset schema for the specified version of the Standard.

    Todo:
        Determine whether a version should be provided.

    """
    path = iati.resources.get_ruleset_path(iati.resources.FILE_RULESET_SCHEMA_NAME)
    schema_str = iati.utilities.load_as_string(path)

    return json.loads(schema_str)


_SCHEMAS = defaultdict(lambda: defaultdict(dict))
"""A cache of loaded Schemas.

This removes the need to repeatedly load a Schema from disk each time it is accessed.

{
    "version_number_a": {
        "populated": {
            "iati-activities": iati.ActivitySchema
            "iati-organisations": iati.OrganisationSchema
        },
        "unpopulated": {
            "iati-activities": iati.ActivitySchema
            "iati-organisations": iati.OrganisationSchema
        },
    },
    "version_number_b": {
        [...]
    },
    [...]
}

Warning:
    Modifying values directly obtained from this cache can potentially cause unexpected behavior. As such, it is highly recommended to perform a `deepcopy()` on any accessed Schema before it is modified in any way.

"""


def _populate_schema(schema, version):
    """Populate a Schema with all its extras.

    The extras include Codelists and Rulesets.

    Args:
        schema (iati.Schema): The Schema to populate.
        version (str): The Integer or Decimal version of the Standard to return the Schema for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.

    Returns:
        iati.Schema: The provided Schema, populated with additional information.

    Warning:
        Does not create a copy of the provided Schema, instead adding to it directly.

    """
    version = _specific_version_for(version)

    codelists_to_add = codelists(version)
    for codelist_to_add in codelists_to_add.values():
        schema.codelists.add(codelist_to_add)

    schema.rulesets.add(ruleset(version))

    return schema


def _schema(path_func, schema_class, version, populate=True, use_cache=False):
    """Return the default Schema of the specified type for the specified version of the Standard.

    Args:
        path_func (func): A function to return the paths at which the relevant Schema can be found.
        schema_class (type): A class definition for the Schema of interest.
        version (str): The Integer or Decimal version of the Standard to return the Schema for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.
        populate (bool): Whether the Schema should be populated with auxilliary information such as Codelists and Rulesets.
        use_cache (bool): Whether the cache should be used rather than loading the Schema from disk again. If used, a `deepcopy()` should be performed on any returned Schema before it is modified.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        iati.Schema: An instantiated IATI Schema for the specified version.

    """
    population_key = 'populated' if populate else 'unpopulated'

    version = _specific_version_for(version)

    schema_paths = path_func(version)

    if (schema_class.ROOT_ELEMENT_NAME not in _SCHEMAS[version][population_key].keys()) or not use_cache:
        schema = schema_class(schema_paths[0])
        if populate:
            schema = _populate_schema(schema, version)
        _SCHEMAS[version][population_key][schema_class.ROOT_ELEMENT_NAME] = schema

    return _SCHEMAS[version][population_key][schema_class.ROOT_ELEMENT_NAME]


def activity_schema(version, populate=True):
    """Return the default Activity Schema for the specified version of the Standard.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Activity Schema for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.
        populate (bool): Whether the Schema should be populated with auxilliary information such as Codelists and Rulesets.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        iati.ActivitySchema: An instantiated IATI Schema for the specified version of the Standard.

    """
    return _schema(iati.resources.get_all_activity_schema_paths, iati.ActivitySchema, version, populate)


def organisation_schema(version, populate=True):
    """Return the default Organisation Schema for the specified version of the Standard.

    Args:
        version (str): The Integer or Decimal version of the Standard to return the Organisation Schema for. If an Integer Version is specified, uses the most recent Decimal Version within the Integer Version.
        populate (bool): Whether the Schema should be populated with auxilliary information such as Codelists and Rulesets.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        iati.OrganisationSchema: An instantiated IATI Schema for the specified version of the Standard.

    """
    return _schema(iati.resources.get_all_organisation_schema_paths, iati.OrganisationSchema, version, populate)
