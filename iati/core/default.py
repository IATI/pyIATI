"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.

    Implement more than Codelists.

"""
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
        iati.core.Codelist: A Codelist with the specified name.

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
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.core.Codelist() instances.

    Warning:
        Further exploration needs to be undertaken in how to handle multiple versions of the Standard.

        The `bypass_cache` parameter could potentially be implemented in a cleaner manner. It also shouldn't really exist until a clear use-case is defined - changes elsewhere in the library may make it redundant.

    Todo:
        Actually handle versions, including errors.

        Test a cache bypass where data is updated.

        Add a function to return a single Codelist by name.

    """
    paths = iati.core.resources.get_all_codelist_paths()

    for path in paths:
        _, filename = os.path.split(path)
        name = filename[:-len(iati.core.resources.FILE_CODELIST_EXTENSION)]  # Get the name of the codelist, without the '.xml' file extension
        if (name not in _CODELISTS.keys()) or bypass_cache:
            xml_str = iati.core.resources.load_as_string(path)
            codelist_found = iati.core.Codelist(name, xml=xml_str)
            _CODELISTS[name] = codelist_found

    return _CODELISTS


_SCHEMAS = {}
"""A cache of loaded Schemas.

This removes the need to repeatedly load a Schema from disk each time it is accessed.

"""


def schemas(bypass_cache=False):
    """Locate all the default IATI Schemas and return them within a dictionary.

    Args:
        bypass_cache (bool): Whether the cache should be bypassed, instead reloading data from disk even if it's already been loaded.

    Returns:
        dict: A dictionary containing all the Schemas for versions of the Standard. The name of the schema the key. An iati.core.Schema() is each value.

    Warning:
        The `bypass_cache` parameter could potentially be implemented in a cleaner manner. It also shouldn't really exist until a clear use-case is defined - changes elsewhere in the library may make it redundant.

    Todo:
        Handle the difference between Organisation and Activity Schemas - i.e. load ActivitySchema or OrganisationSchema, rather than always ActivitySchema

        Consider the Schema that defines the format of Codelists.

        Test a cache bypass where data is updated.

        Load the Schemas.

        Needs to handle multiple versions of the Schemas. Versions could perhaps be placed within a nested dictionary, with the version number as the key.

    """
    schema_paths_by_type = {
        'activity': iati.core.resources.get_all_activity_schema_paths(),
        'organisation': iati.core.resources.get_all_organisation_schema_paths()
    }

    for schema_type, schema_paths in schema_paths_by_type.items():
        for path in schema_paths:
            name = path.split(os.sep).pop()[:-len(iati.core.resources.FILE_SCHEMA_EXTENSION)]
            if (name not in _SCHEMAS.keys()) or bypass_cache:
                if schema_type == 'activity':
                    schema = iati.core.ActivitySchema(path)
                elif schema_type == 'organisation':
                    schema = iati.core.OrganisationSchema(path)
                _SCHEMAS[name] = schema

    return _SCHEMAS


def schema(name, version=None):
    """Return a default Schema with the specified name for the specified version of the Standard.

    Args:
        name (str): The name of the Schema to locate.
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that the latest version of the Schema is returned.

    Returns:
        iati.core.schema.Schema (or subclass): An instance of the schema corresponding to the input name and version.

    Raises:
        KeyError: If the input schema name is not found as part of the default IATI Schemas.

    Todo:
        Needs to handle multiple versions of the Schemas. At present, only the latest version can be returned.

    """

    try:
        return schemas()[name]
    except KeyError:
        msg = 'There is no default Schema in version {0} of the Standard with the name {1}.'.format(version, name)
        iati.core.utilities.log_warning(msg)
        raise ValueError(msg)
