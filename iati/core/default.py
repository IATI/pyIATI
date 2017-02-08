"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.

    Implement more than Codelists.
"""
import os
import iati.core.codelists
import iati.core.resources


_codelists = {}
"""A cache of loaded Codelists.

This removes the need to repeatedly load a Codelist from disk each time it is accessed.
"""

def codelists(version=0, bypass_cache=False):
    """Locate the default Codelists for the specified version of the Schema.

    Args:
        version (float): The version of the Standard to return the Codelists for. Defaults to 0. This means that the latest version of the Codelist is returned.
        bypass_cache (bool): Whether the cache should be bypassed, instead reloading data from disk even if it's already been loaded.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included.
            The Codelist name is the key. An iati.core.codelists.Codelist() is each value.

    Todo:
        Actually handle versions, including errors.
    """
    paths = iati.core.resources.find_all_codelist_paths()

    for path in paths:
        name = path.split(os.sep).pop()[:-4]
        if (not name in _codelists.keys()) or bypass_cache:
            xml_str = iati.core.resources.load_as_string(path)
            codelist = iati.core.codelists.Codelist(name, xml=xml_str)
            _codelists[name] = codelist

    return _codelists
