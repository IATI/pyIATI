"""Configuration to exist in the global scope for pytest."""
import collections
import pytest
import iati.default
import iati.resources
import iati.tests.utilities


@pytest.fixture(params=[
    ('2.02', 62),  # There are 38 embedded codelists at v2.02, plus 24 non-embedded codelists (which are valid for any version)
    ('2.01', 61),  # There are 37 embedded codelists at v2.01, plus 24 non-embedded codelists (which are valid for any version)
    ('1.05', 59),  # There are 35 embedded codelists at v1.05, plus 24 non-embedded codelists (which are valid for any version)
    ('1.04', 59)  # There are 35 embedded codelists at v1.04, plus 24 non-embedded codelists (which are valid for any version)
])
def codelist_lengths_by_version(request):
    """Return a tuple containing versions of the Standard, and the number of Codelists for that version.

    Format: `(version=[standardVersion], expected_length=[numCodelists])`

    """
    output = collections.namedtuple('output', 'version expected_length')
    return output(version=request.param[0], expected_length=request.param[1])


@pytest.fixture
def schema_ruleset():
    """Return a schema with the Standard Ruleset added.

    Returns:
        A valid Activity Schema with the Standard Ruleset added.

    Todo:
        Stop this being fixed to 2.02.

    """
    schema = iati.default.activity_schema('2.02', False)
    ruleset = iati.default.ruleset('2.02')

    schema.rulesets.add(ruleset)

    return schema


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_SUPPORTED)
def standard_version_mandatory(request):
    """Return a list that can be passed to a function using the argument list unpacking functionality.

    For more information about unpacking argument lists, see https://docs.python.org/3.6/tutorial/controlflow.html#unpacking-argument-lists

    Example:
        The returned list can be used to test functions (such as `iati.default.codelists`) which has an optional parameter for the version, or can expect `version=None`. It has an optional parameter after the version.
        In this case test usage would be `iati.default.codelists(*standard_version_mandatory)`.

    Returns:
        list: A string which corresponds to a version of the Standard.

    """
    return [request.param]


@pytest.fixture(params=[
    '1.00', '1.0', '2.0', '2.00',  # integer with a zero decimal
    '1.050', '2.020',  # valid version with extra 0
    '1.06', '2.03',  # the next decimal within valid integers
    '1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2',  # valid versions with the 0 after the decimal point missing
    '3.0', '3.0.0', '3.00', '3.01', '3.1',  # the first few potential values for the next integer
    1.01, 1.02, 1.03, 1.04, 1.05, 2.01, 2.02,  # valid version numbers, but numerical rather than strings
    1, 2  # valid integer versions, but numerical rather than strings
] + iati.tests.utilities.generate_test_types(['none'], True)  # fuzzing data
)
def std_version_invalid(request):
    """Return a string that isn't a version number, instead being an invalid value."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_MAJOR)
def standard_version_major(request):
    """Return a major version of the IATI Standard."""
    return str(request.param)


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS)
def standard_version_all(request):
    """Return a version of the IATI Standard."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_SUPPORTED)
def standard_version_optional(request):
    """Return a list that can be passed to a function using the argument list unpacking functionality.

    For mor information about unpacking argument lists, see https://docs.python.org/3.6/tutorial/controlflow.html#unpacking-argument-lists

    Example:
        The returned list can be used to test functions (such as `get_codelist_paths`) which has an optional parameter for the version, or can expect `version=None`.,
        In this case test usage would be `get_codelist_paths(*standard_version_optional)`.

    Returns:
        list: Either i) an empty list, ii) a list containing None, or iii) a string which corresponds to a version of the Standard.

    """
    return [request.param]


_CMP_FUNC_EQUAL_VAL = [
    lambda x, y: x == y,
    lambda x, y: y == x
]


_CMP_FUNC_EQUAL_HASH = [
    lambda x, y: hash(x) == hash(y)
]


_CMP_FUNC_DIFFERENT_VAL = [
    lambda x, y: x != y,
    lambda x, y: y != x
]


_CMP_FUNC_DIFFERENT_HASH = [
    lambda x, y: hash(x) != hash(y)
]


@pytest.fixture(params=_CMP_FUNC_EQUAL_VAL)
def cmp_func_equal_val(request):
    """Return a comparison function that checks whether two values are equal."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_EQUAL_HASH)
def cmp_func_equal_hash(request):
    """Return a comparison function that checks whether two values have the same hash."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_EQUAL_VAL + _CMP_FUNC_EQUAL_HASH)
def cmp_func_equal_val_and_hash(request):
    """Return a comparison function that checks whether two values are equal and have the same hash."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_VAL)
def cmp_func_different_val(request):
    """Return a comparison function that checks whether two values are different."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_HASH)
def cmp_func_different_hash(request):
    """Return a comparison function that checks whether two hashes are different."""
    return request.param


@pytest.fixture(params=_CMP_FUNC_DIFFERENT_VAL + _CMP_FUNC_DIFFERENT_HASH)
def cmp_func_different_val_and_hash(request):
    """Return a comparison function that checks whether two values are different and have different hashes."""
    return request.param
