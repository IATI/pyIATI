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

def codelists(version=0):
    """Locate the default Codelists for the specified version of the Schema.

    Args:
        version (float): The version of the Standard to return the Codelists for. Defaults to 0. This means that the latest version of the Codelist is returned.

    Raises:
        ValueError: When a specified version is not a valid version of the IATI Standard.

    Returns:
        dict: A dictionary containing all the Codelists at the specified version of the Standard. All Non-Embedded Codelists are included.
            The Codelist name is the key. An iati.core.codelists.Codelist() is each value.

    Todo:
        Actually handle versions, including errors.

        Improve caching.
    """
    paths = iati.core.resources.find_all_codelist_paths()

    for path in paths:
        xml_str = iati.core.resources.load_as_string(path)
        name = path.split(os.sep).pop()[:-4]
        codelist = iati.core.codelists.Codelist(name, xml=xml_str)
        _codelists[name] = codelist

    return _codelists
