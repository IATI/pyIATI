"""A module containing utility constants and functions for tests.

A large number of constants containing example file content are contained. These constants are named from left to right, with general properties first, then leading into more specific information. These names indicate what they are used for.

Example:
    To load a file into a string::

        name_of_file = 'a-file-name-without-the-extension'
        CONSTANT_NAME = load_as_string(name_of_file)

Note:
    The current method of managing test data is known to be sub-optimal. Suggestions for better methods that satisfy requirements are appreciated!

Todo:
    Add versions of constants that are valid for differing schema versions.

"""
import decimal
from lxml import etree
import iati.resources
import iati.constants
import iati.tests.resources


# This will need updating once test data forcing XML format is fixed
RULESET_FOR_TESTING = iati.Ruleset(iati.utilities.load_as_string(iati.resources.get_ruleset_path('ruleset_for_tests')))
"""A working Ruleset based on the Standard Ruleset."""


SCHEMA_ACTIVITY_NAME_VALID = 'iati-activities-schema'
"""A string containing a valid IATI Activity Schema name."""
SCHEMA_ORGANISATION_NAME_VALID = 'iati-organisations-schema'
"""A string containing a valid IATI Organisaion Schema name."""
SCHEMA_NAME_VALID = 'iati-activities-schema'
"""A string containing a valid Schema name."""

XML_TREE_VALID = etree.fromstring(iati.utilities.load_as_string(iati.tests.resources.get_test_data_path('valid_not_iati')))
"""An etree that is valid XML but not IATI XML."""
XML_TREE_VALID_IATI = etree.fromstring(iati.utilities.load_as_string(iati.tests.resources.get_test_data_path('valid_iati')))
"""A valid IATI etree."""
XML_TREE_VALID_IATI_INVALID_CODE = etree.fromstring(iati.utilities.load_as_string(iati.tests.resources.get_test_data_path('valid_iati_invalid_code')))
"""A valid IATI etree that has an invalid Code value."""


TYPE_TEST_DATA = {
    'bool': [True, False],
    'bytes': [],  # counts as a string, so moved there
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
    'none': [None],
    'other': [NotImplemented],
    'range': [range(3, 4)],
    'set': [set(range(20)), set(['hello', 23]), frozenset(range(20)), frozenset(['hello', 23])],
    'str': [b'\x80abc', b'\x80abc', '\N{GREEK CAPITAL LETTER DELTA}', '\u0394', '\U00000394', 'This is a string'],  # python2.7 warning # pylint: disable=anomalous-unicode-escape-in-string
    'tuple': [(), (1, 2)],
    'type': [type(1), type('string')],
    'unicode': [],  # counts as a string, so moved there
    'view': [{}.keys(), dict(zip(['one', 'two', 'three'], [1, 2, 3])).items(), dict(one=1, two=2, three=3).values()]
}
"""Generic test data of various Python builtin types."""


def generate_test_types(types, invert_types=False):
    """Find a number of values of the specified type to pass to a test function.

    Args:
        types (list of str): The types of parameter that should be looked for.
        invert_types (bool): Whether to invert the list of types being looked for, instead returning everything else. Default False.

    Returns:
        list: A list of values to pass to the test function.

    """
    valid_keys_as_specified = [key for key in types if key in TYPE_TEST_DATA]
    if invert_types:
        valid_keys = [key for key in TYPE_TEST_DATA if key not in valid_keys_as_specified]
    else:
        valid_keys = valid_keys_as_specified

    valid_keys = sorted(valid_keys)

    results = []

    for key in valid_keys:
        results = results + TYPE_TEST_DATA[key]

    return results
