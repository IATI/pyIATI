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
import iati.core.resources


def load_as_dataset(file_path):
    """Load a specified test data file as a Dataset.

    Args:
        file_path (str): The path of the file, relative to the root test data folder. Folders should be separated by a forward-slash (`/`).

    Returns:
        dataset: A Dataset containing the contents of the file at the specified location.

    Raises:
        iati.core.exceptions.ValidationError: If the provided XML does not conform to the IATI standard.

    """
    return iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path(file_path))


def load_as_string(file_path):
    """Load a specified test data file as a string.

    Args:
        file_path (str): The path of the file, relative to the root test data folder. Folders should be separated by a forward-slash (`/`).

    Returns:
        str (python3) / unicode (python2): The contents of the file at the specified location.

    """
    return iati.core.resources.load_as_string(iati.core.resources.get_test_data_path(file_path))


DATASET_FOR_ATLEASTONE_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_atleastone'))
"""A Dataset that is permitted by `RuleAtLeastOne`."""
DATASET_FOR_ATLEASTONE_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_atleastone'))
"""A Dataset that is not permitted by `RuleAtLeastOne`."""

DATASET_FOR_DATEORDER_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_dateorder'))
"""A Dataset that is permitted by `RuleDateOrder`."""
DATASET_FOR_DATEORDER_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_dateorder'))
"""A Dataset that is not permitted by `RuleDateOrder`."""
DATASET_FOR_DATEORDER_RULE_INVALID_DATE_FORMAT = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_format_dateorder'))
"""A Dataset that contains dates that are formatted incorrectly according to RuleDateOrder."""

DATASET_FOR_DEPENDENT_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_dependent'))
"""A Dataset that is permitted by `RuleDependent`."""
DATASET_FOR_DEPENDENT_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_dependent'))
"""A Dataset that is not permitted by `RuleDependent`."""

DATASET_FOR_NOMORETHANONE_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_nomorethanone'))
"""A Dataset that is permitted by `RuleNoMoreThanOne`."""
DATASET_FOR_NOMORETHANONE_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_nomorethanone'))
"""A Dataset that is not permitted by `RuleNoMoreThanOne`."""

DATASET_FOR_REGEXMATCHES_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_regexmatches'))
"""A Dataset that is permitted by `RuleRegexMatches`."""
DATASET_FOR_REGEXMATCHES_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_regexmatches'))
"""A Dataset that is not permitted by `RuleRegexMatches`."""

DATASET_FOR_REGEXNOMATCHES_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_regexnomatches'))
"""A Dataset that is permitted by `RuleRegexNoMatches`."""
DATASET_FOR_REGEXNOMATCHES_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_regexnomatches'))
"""A Dataset that is not permitted by `RuleRegexNoMatches`."""

DATASET_FOR_STARTSWITH_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_startswith'))
"""A Dataset that is permitted by `RuleStartsWith`."""
DATASET_FOR_STARTSWITH_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_startswith'))
"""A Dataset that is not permitted by `RuleStartsWith`."""

DATASET_FOR_SUM_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_sum'))
"""A Dataset that is permitted by `RuleSum`."""
DATASET_FOR_SUM_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_sum'))
"""A Dataset that is not permitted by `RuleSum`."""

DATASET_FOR_UNIQUE_RULE_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_unique'))
"""A Dataset that is permitted by `RuleUnique`."""
DATASET_FOR_UNIQUE_RULE_INVALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_unique'))
"""A Dataset that is not permitted by `RuleUnique`."""

DATASET_FOR_STANDARD_RULESET_VALID = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('valid_std_ruleset'))
"""A Dataset that meets the IATI Standard ruleset."""
DATASET_FOR_STANDARD_RULESET_INVALID_BAD_DATE_ORDER = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_std_ruleset_bad_date_order'))
"""A Dataset that does not meet the IATI Standard ruleset (on account of a bad date order)."""
DATASET_FOR_STANDARD_RULESET_INVALID_BAD_IDENTIFIER = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_std_ruleset_bad_identifier'))
"""A Dataset that does not meet the IATI Standard ruleset (on account of a bad IATI identifier)."""
DATASET_FOR_STANDARD_RULESET_INVALID_DOES_NOT_SUM_100 = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_std_ruleset_does_not_sum_100'))
"""A Dataset that does not meet the IATI Standard ruleset (on account of a sums not adding to 100%)."""
DATASET_FOR_STANDARD_RULESET_INVALID_MISSING_SECTOR_ELEMENT = iati.core.resources.load_as_dataset(iati.core.resources.get_test_data_path('invalid_std_ruleset_missing_sector_element'))
"""A Dataset that does not meet the IATI Standard ruleset (on account of a missing sector element)."""

SCHEMA_NAME_VALID = 'iati-activities-schema'
"""A string containing a valid Schema name."""


XML_TREE_VALID = etree.fromstring(load_as_string('valid_not_iati'))


SCHEMA_ACTIVITY_NAME_VALID = 'iati-activities-schema'
"""A string containing a valid IATI Activity Schema name."""
SCHEMA_ORGANISATION_NAME_VALID = 'iati-organisations-schema'
"""A string containing a valid IATI Organisaion Schema name."""

XML_TREE_VALID = etree.fromstring(load_as_string('valid_not_iati'))
"""An etree that is not valid IATI data."""
XML_TREE_VALID_IATI = etree.fromstring(load_as_string('valid_iati'))
"""A valid IATI etree."""
XML_TREE_VALID_IATI_INVALID_CODE = etree.fromstring(load_as_string('valid_iati_invalid_code'))
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
    'str': [b'\x80abc', b'\x80abc', '\N{GREEK CAPITAL LETTER DELTA}', '\u0394', '\U00000394', 'This is a string'],
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
