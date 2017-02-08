"""A module to provide a copy of all the default data within the IATI SSOT.

This includes Codelists, Schemas and Rulesets at various versions of the Standard.

Todo:
    Handle multiple versions of the Standard rather than limiting to the latest.
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
        Implement this.
    """
    pass
