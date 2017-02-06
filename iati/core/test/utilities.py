"""A module containing utility constants and functions for tests.

Todo:
    Add versions of constants that are valid for differing schema versions.
"""
from lxml import etree

SCHEMA_NAME_VALID = 'iati-activities-schema'
"""A string containing a valid Schema name."""

XML_STR_VALID = '<parent><child attribute="value" /></parent>'
"""A string containing valid XML that is not valid against the IATI schema."""
XML_STR_VALID_IATI = None
"""A string containing valid IATI XML.

Todo:
    Create a valid IATI XML string.
"""
XML_STR_INVALID = 'This is a string that is not valid XML'
"""A string that is not valid XML."""

XML_TREE_VALID = etree.fromstring(XML_STR_VALID)
"""An etree that is not valid IATI data."""
XML_TREE_VALID_IATI = None
"""A valid IATI etree.

Todo:
    Create a valid IATI XML etree.
"""
