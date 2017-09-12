"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.

    Implement more than Codelists.

"""
from copy import deepcopy
import os
import iati.core.codelists
import iati.core.constants
import iati.core.resources


def get_default_version_if_none(version):
    """Returns the default version number if the input version is None. Otherwise returns the input version as is.

    Args:
        version (str or None): The version to test against.

    Returns:
        str or version: The default version if the input version is None.  Otherwise returns the input version.
    """
    if version is None:
        return iati.core.constants.STANDARD_VERSION_LATEST
    else:
        return version


_CODELISTS = {}
"""A cache of loaded Codelists.

This removes the need to repeatedly load a Codelist from disk each time it is accessed.

Warning:
    Modifying values directly obtained from this cache can potentially cause unexpected behavior. As such, it is highly recommended to perform a `deepcopy()` on any accessed Codelist before it is modified in any way.

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
        Better distinguish the types of ValueError.

        Better distinguish TypeErrors from KeyErrors - sometimes the latter is raised when the former should have been.

    """
    try:
        codelist_found = _codelists(version, True)[name]
        return deepcopy(codelist_found)
    except (KeyError, TypeError):
        msg = "There is no default Codelist in version {0} of the Standard with the name {1}.".format(version, name)
        iati.core.utilities.log_warning(msg)
        raise ValueError(msg)


def _codelists(version=None, use_cache=False):
    """Locate the default Codelists for the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that the latest version of the Codelist is returned.
        use_cache (bool): Whether the cache should be used rather than loading the Codelists from disk again. If used, a `deepcopy()` should be performed on any returned Codelist before it is modified.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.core.Codelist() instances.

    Warning:
        Setting `use_cache` to `True` is dangerous since it does not return a deep copy of the Codelists. This means that modification of a returned Codelist will modify the Codelist everywhere.
        A `deepcopy()` should be performed on any returned value before it is modified.

    Note:
        This is a private function so as to prevent the (dangerous) `use_cache` parameter being part of the public API.

    """
    version = get_default_version_if_none(version)

    paths = iati.core.resources.get_all_codelist_paths(version)

    for path in paths:
        _, filename = os.path.split(path)
        name = filename[:-len(iati.core.resources.FILE_CODELIST_EXTENSION)]  # Get the name of the codelist, without the '.xml' file extension
        codelists_by_version = _CODELISTS.get(version, {})
        if (name not in codelists_by_version.keys()) or not use_cache:
            xml_str = iati.core.resources.load_as_string(path)
            codelist_found = iati.core.Codelist(name, xml=xml_str)
            codelists_by_version[name] = codelist_found
            _CODELISTS[version] = codelists_by_version

    return _CODELISTS[version]


def codelists(version=None):
    """Locate the default Codelists for the specified version of the Standard.

    Args:
        version (str): The version of the Standard to return the Codelists for. Defaults to None. This means that the latest version of the Codelist is returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included. Keys are Codelist names. Values are iati.core.Codelist() instances.

    """
    return _codelists(version)



_SCHEMAS = {}
"""A cache of loaded Schemas.

This removes the need to repeatedly load a Schema from disk each time it is accessed.

Warning:
    Modifying values directly obtained from this cache can potentially cause unexpected behavior. As such, it is highly recommended to perform a `deepcopy()` on any accessed Schema before it is modified in any way.

"""


def _activity_schema(version=None, use_cache=False):
    """Return a dictionary of the default ActivitySchema objects for all versions of the Standard.

    Args:
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that the latest version of the Schema is returned.
        use_cache (bool): Whether the cache should be used rather than loading the Schema from disk again. If used, a `deepcopy()` should be performed on any returned Schema before it is modified.

    Returns:
        dict: Containing the version (as keys) and a corresponding ActivitySchema object (as values).

    """
    output = {}

    version = get_default_version_if_none(version)

    activity_schema_paths = iati.core.resources.get_all_activity_schema_paths(version)
    # import pdb;pdb.set_trace()
    if ('iati-activities-schema' not in _SCHEMAS.get(version, {}).keys()) or not use_cache:
        if version not in _SCHEMAS.keys():
            _SCHEMAS[version] = {}
        _SCHEMAS[version]['iati-activities-schema'] = iati.core.ActivitySchema(activity_schema_paths[0])

    output[version] = _SCHEMAS[version]['iati-activities-schema']

    return output[version]


def activity_schema(version=None):
    """Return a dictionary of the default ActivitySchema objects for all versions of the Standard.

    Args:
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that the latest version of the Schema is returned.

    Returns:
        dict: Containing the version (as keys) and a corresponding ActivitySchema object (as values).

    """
    return _activity_schema(version)


def _organisation_schema(version=None, use_cache=False):
    """Return a dictionary of the default OrganisationSchema objects for all versions of the Standard.

    Args:
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that the latest version of the Schema is returned.
        use_cache (bool): Whether the cache should be used rather than loading the Schema from disk again. If used, a `deepcopy()` should be performed on any returned Schema before it is modified.

    Returns:
        dict: Containing the version (as keys) and a corresponding OrganisationSchema object (as values).

    """
    output = {}

    version = get_default_version_if_none(version)

    organisation_schema_paths = iati.core.resources.get_all_org_schema_paths(version)
    if ('iati-organisations-schema' not in _SCHEMAS.get(version, {}).keys()) or not use_cache:
        if version not in _SCHEMAS.keys():
            _SCHEMAS[version] = {}
        _SCHEMAS[version]['iati-organisations-schema'] = iati.core.OrganisationSchema(organisation_schema_paths[0])

    output[version] = _SCHEMAS[version]['iati-organisations-schema']

    return output[version]


def organisation_schema(version=None):
    """Return a dictionary of the default OrganisationSchema objects for all versions of the Standard.

    Args:
        version (str): The version of the Standard to return the Schema for. Defaults to None. This means that the latest version of the Schema is returned.

    Returns:
        dict: Containing the version (as keys) and a corresponding OrganisationSchema object (as values).

    """
    return _organisation_schema(version)
