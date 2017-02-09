"""A module containing utility constants and functions for tests.

Todo:
    Add versions of constants that are valid for differing schema versions.
"""
import decimal
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

TYPE_TEST_DATA = {
    'bool': [True, False],
    'bytes': [b'\x80abc', b'\x80abc'],
    'bytearray': [bytearray.fromhex('2Ef0 F1f2  '), bytearray(b'Hi!'), bytearray(range(20))],
    'complex': [3453J, -35415J, 0J, complex(234, 681), complex(-768, 16078), complex(6187, -81), complex(-1867, -618)],
    'contextmanager': [decimal.localcontext()],
    'float': [-2343324.534, 0.0, 32423.34, 1.3e7, float('Infinity'), float('nan'), float('-inf')],
    'function': [dir, hash, map, max, type],
    'int': [-234, 0, 2131908],
    'iter': [iter([1, 2, 3])],
    'list': [[], [1, 23], ['varying', 7, b'ypes', []]],
    'mapping': [{}, dict(zip(['one', 'two', 'three'], [1, 2, 3])), dict(one=1, two=2, three=3)],
    'memory': [memoryview(b'abcefg')],
    'other': [None, NotImplemented, ...],
    'range': [range(3, 4)],
    'set': [set(range(20)), set(['hello', 23]), frozenset(range(20)), frozenset(['hello', 23])],
    'str': [SCHEMA_NAME_VALID, XML_STR_VALID, XML_STR_INVALID],
    'tuple': [(), (1, 2)],
    'type': [type(1), type('string')],
    'unicode': ["\N{GREEK CAPITAL LETTER DELTA}", "\u0394", "\U00000394"],
    'view': [{}.keys(), dict(zip(['one', 'two', 'three'], [1, 2, 3])).items(), dict(one=1, two=2, three=3).values()]
}
"""Generic test data of various Python builtin types."""


def find_parameter_by_type(types, type_as_specified=True):
    """Find a number of values of the specified type to pass to a test function.

    Args:
        types (list of str): The types of parameter that should be looked for.
        type_as_specified (bool): Whether to look for values as specified or everything else. Default True.

    Returns:
        list: A list of values to pass to the test function.
    """
    valid_keys_as_specified = [key for key in types if key in TYPE_TEST_DATA]
    if not type_as_specified:
        valid_keys = [key for key in TYPE_TEST_DATA.keys() if key not in valid_keys_as_specified]
    else:
        valid_keys = valid_keys_as_specified

    results = []

    for key in valid_keys:
        results = results + TYPE_TEST_DATA[key]

    return results
