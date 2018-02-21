"""Pytest fixtures for specifying versions.

---

There is a standard method of defining fixtures that return version numbers. This is:

    `std_ver_[component_level]_[instantiation_status]_[validity]_[type(s)]_[knowledge]`

Each of these sections has a number of values that they may take. It is not necessary to state all sections for every fixture. Some sections may have multiple values.

* Component levels
  * `major` - major / integer versions
  * `minor` - minor / decimal versions
  * `all` - both major and minor versions
  * `independent` - a value that represents every single version
* Instantiation Status
  * `inst` - an iati.Version instance
  * `uninst` - something that is not an iati.Version instance
  * `mixedinst` - a mix of iati.Version instances and other types
* Validity
  * `valid` - a value that represents a version number
  * `valueerr` - a value of a type that could represent a version number, but the value is not in the correct format or range
  * `typeerr` - a value of a type that cannot represent a version number
  * `mixederr` - a mix of values that cause each Value and Type errors
* Type(s) (for uninstantiated values)
  * `str` - strings
  * `int` - integers
  * `iativer` - strings in the IATIver format
  * `semver` - strings in the SemVer format
  * `decimal` - decimal.Decimal instances
* Knowledge
  * `known` - pyIATI knows that this is an approved version of the IATI Standard that exists
  * `unknown` - pyIATI does not that this is an approved version of the IATI Standard that exists
  * `possible` - a known or unknown version number
  * `fullsupport` - pyIATI fully supports this version - this includes Schemas, Codelists, Rulesets, validation and more
  * `partsupport` - pyIATI partially supports this version - this may mean that there is a Schema, but not the other components
  * `single` - a fixture that will only parameterize with a single value
  * `v0` - a version number with a major component of 0
  * `v1` - a version number with a major component of 1
  * `v2` - a version number with a major component of 2

"""
from decimal import Decimal
import itertools
import pytest
import iati.constants


def generate_semver_list(major_components, minor_components, patch_components):
    """Generate a list of SemVer-format values.

    Params:
        major_components (list of int): List of values to use as the Major Component in the generated Version Numbers.
        minor_components (list of int): List of values to use as the Minor Component in the generated Version Numbers.
        patch_components (list of int): List of values to use as the Patch Component in the generated Version Numbers.

    Returns:
        list of string: List of values in the SemVer format.
    """
    return [semver(version[0], version[1], version[2]) for version in itertools.product(major_components, minor_components, patch_components)]


def iativer(integer, decimal):
    """Construct an IATIver-format version number.

    Args:
        integer (int): The integer component of the version number.
        decimal (int): The decimal component of the version number.

    Returns:
        str: An IATIver-format version number with the specified Integer and Decimal Components.
    """
    return str(integer) + '.0' + str(decimal)


def semver(major, minor, patch):
    """Construct an SemVer-format version number.

    Args:
        major (int): The major component of the version number.
        minor (int): The minor component of the version number.
        patch (int): The patch component of the version number.

    Returns:
        str: A SemVer-format version number with the specified Major, Minor and Patch Components.
    """
    return '.'.join([str(major), str(minor), str(patch)])


def split_decimal(version_decimal):
    """Split a Decimal version number into numeric representations of its components.

    Args:
        version_decimal (Decimal): A Decimal containing an IATI version number.

    Returns:
        list of int: A list containing numeric representations of the Integer and Decimal components.
    """
    integer_component = int(version_decimal)
    decimal_component = int(version_decimal * 100) - 100

    return [integer_component, decimal_component]


def split_iativer(version_str):
    """Split an IATIver-format version number into numeric representations of its components.

    Args:
        version_str (string): An IATIver-format string.

    Returns:
        list of int: A list containing numeric representations of the Integer and Decimal components.
    """
    integer_component = int(version_str.split('.')[0])
    decimal_component = int(version_str.split('.')[1])

    return [integer_component, decimal_component]


def split_semver(version_str):
    """Split a SemVer-format version number into numeric representations of its components.

    Args:
        version_str (string): A SemVer-format string.

    Returns:
        list of int: A list containing numeric representations of the Major, Minor and Patch components.
    """
    major_component = int(version_str.split('.')[0])
    minor_component = int(version_str.split('.')[1])
    patch_component = int(version_str.split('.')[2])

    return [major_component, minor_component, patch_component]


ZERO_TO_LOTS = list(range(0, 220, 51))
"""A list of numbers from 0 to a large number. 0 is included."""
ONE_TO_NINE = list(range(1, 10))
"""A list of numbers from 1-9 inclusive."""
ONE_TO_LOTS = list(range(1, 220, 51))
"""A list of numbers from 1 to a large number. 1 is included."""
TWO_TO_LOTS = list(range(2, 220, 51))
"""A list of numbers from 2 to a large number. 2 is included."""
TEN_TO_LOTS = list(range(10, 220, 51))
"""A list of numbers from 10 to a large number. 10 is included."""
NEGATIVE_NUMBERS = list(range(-10, 0))
"""A list of negative numbers."""
NON_POSITIVE_NUMBERS = NEGATIVE_NUMBERS + [0]
"""A list of negative numbers and zero."""


MINOR_DECIMAL_VALID = [
    Decimal('1.0' + str(minor)) for minor in ONE_TO_NINE  # base permitted values
] + [
    Decimal('1.010')  # equivalent to `Decimal('1.01')`
]
"""list of Decimal: A list of valid Decimal version numbers."""

MINOR_DECIMAL_INVALID = [
    Decimal('1.0' + str(minor + 1)) for minor in TEN_TO_LOTS  # values greater than 10
] + [
    Decimal('1.00')  # lower boundary case
] + [
    Decimal('1.' + str(minor)) for minor in TEN_TO_LOTS  # no zero after decimal point
] + [
    Decimal(iativer(components[0], components[1])) for components in
    list(itertools.product(TWO_TO_LOTS, ONE_TO_LOTS)) +  # major versions above 1
    list(itertools.product(NON_POSITIVE_NUMBERS, ONE_TO_LOTS))  # major versions below 1
]
"""list of Decimal: A list of invalid Decimal version numbers."""

MINOR_IATIVER_VALID = [
    iativer(components[0], components[1]) for components in
    list(itertools.product(ONE_TO_LOTS, ONE_TO_NINE)) +  # decimals from 1-9 inclusive
    list(itertools.product(TWO_TO_LOTS, TEN_TO_LOTS))  # decimals from 10-up for integers from 2 up
]
"""list of str: A list of valid IATIver format version numbers."""

MINOR_IATIVER_INVALID = [
    iativer(components[0], components[1]) for components in  # pylint: disable=undefined-loop-variable
    list(itertools.product([1], TEN_TO_LOTS)) +  # integer 1 may only have decimal 01-09
    list(itertools.product([0], ONE_TO_NINE + TEN_TO_LOTS)) +  # integer value of 0
    list(itertools.product(ONE_TO_LOTS, [0])) +  # decimal value of 0
    list(itertools.product(NEGATIVE_NUMBERS, ONE_TO_NINE)) +  # negative integer
    list(itertools.product(ONE_TO_LOTS, NEGATIVE_NUMBERS))  # negative decimal
] + [
    str(components[0]) + '.' + str(components[1]) for components in itertools.product(ONE_TO_LOTS, ONE_TO_NINE)  # non-padded Decimal  # pylint: disable=undefined-loop-variable
]
"""list of str: A list of values that look like they could be an IATIver-format version number, but are not."""

MINOR_SEMVER_VALID = generate_semver_list(ONE_TO_LOTS, ZERO_TO_LOTS, ZERO_TO_LOTS)
"""list of str: A list of valid SemVer format version numbers."""

MINOR_MIXED_VER_VALID = MINOR_IATIVER_VALID + MINOR_SEMVER_VALID + MINOR_DECIMAL_VALID
"""list of (str / Decimal): A list of valid version numbers of any permitted format."""

MAJOR_VALID_INT = list(range(1, 100, 17))
"""list of int: A list of valid major version numbers represented as integers."""

MAJOR_VALID_STR = [str(ver) for ver in MAJOR_VALID_INT]
"""list of str: A list of valid major version numbers represented as strings."""

MAJOR_VALID = MAJOR_VALID_INT + MAJOR_VALID_STR
"""list of (int / str): A list of values that are valid representations of valid major version numbers."""

MAJOR_INVALID_NEGATIVE = NEGATIVE_NUMBERS + [str(val) for val in NEGATIVE_NUMBERS]
"""list of (int / str): A list of invalid major version numbers. Invalid because they are negative values."""

MAJOR_INVALID_WHITESPACE = [' ' + str(val) + ' ' for val in MAJOR_VALID_STR]
"""list of str: A list of invalid major version numbers. Invalid because there is whitespace."""

MAJOR_INVALID_ZERO = [0, '0']
"""list of (int / str): A list of invalid major version numbers. Invalid because they'd represent version 0."""

MAJOR_INVALID = MAJOR_INVALID_NEGATIVE + MAJOR_INVALID_WHITESPACE + MAJOR_INVALID_ZERO
"""list of (int / str): A list of values that look like they could be valid representations of valid major versions numbers, but are not."""


@pytest.fixture(params=iati.tests.utilities.generate_test_types(['str'], True))
def std_ver_minor_uninst_typeerr(request):
    """Return a value of the wrong type to represent a minor version number."""
    return request.param


@pytest.fixture(params=iati.tests.utilities.generate_test_types([], True))
def std_ver_minor_uninst_mixederr(request):
    """Return a value that does not represent a minor version number."""
    return request.param


@pytest.fixture(params=iati.tests.utilities.generate_test_types(['str', 'none', 'int'], True))
def std_ver_all_uninst_typeerr(request):
    """Return a value of the wrong type to represent a version number.

    Todo:
        Change magic value to be something other than `None`.
        See: https://github.com/IATI/pyIATI/issues/218#issuecomment-364086162

    """
    return request.param


@pytest.fixture(params=MINOR_DECIMAL_VALID)
def std_ver_minor_uninst_valid_decimal_possible(request):
    """Return a decimal value that is a valid representation of a minor version number."""
    return request.param


@pytest.fixture(params=MINOR_DECIMAL_INVALID)
def std_ver_minor_uninst_valueerr_decimal(request):
    """Return a decimal value that is not a valid value to represent a minor version number."""
    return request.param


@pytest.fixture(params=MINOR_IATIVER_VALID)
def std_ver_minor_uninst_valid_iativer_possible(request):
    """Return a string that is a correctly constructed IATIver minor version number."""
    return request.param


@pytest.fixture(params=MINOR_IATIVER_INVALID)
def std_ver_minor_uninst_valueerr_iativer(request):
    """Return a string that looks like it coule be a valid IATIver minor version number, but is not."""
    return request.param


@pytest.fixture(params=MINOR_SEMVER_VALID)
def std_ver_minor_uninst_valid_semver_possible(request):
    """Return a string that is a correctly constructed SemVer minor version number."""
    return request.param


@pytest.fixture(params=generate_semver_list([0], ZERO_TO_LOTS, ZERO_TO_LOTS))
def str_ver_minor_uninst_valueerr_v0(request):
    """Return a value that is a correctly formatted version number, but has a major version of 0.

    Todo:
        Pass in IATIver strings and Decimals with a Major version of 0.

    """
    return request.param


@pytest.fixture(params=MINOR_MIXED_VER_VALID)
def std_ver_minor_uninst_valid_possible(request):
    """Return a valid version number in a valid format."""
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS)
def std_ver_minor_uninst_valid_known(request):
    """Return an uninstantiated IATI version number that pyIATI knows to exist.

    Todo:
        Also return the SemVer and Decimal representations.

    """
    return request.param.iativer_str


@pytest.fixture(params=[
    ver.iativer_str for ver in iati.constants.STANDARD_VERSIONS_SUPPORTED
] + [
    ver.semver_str for ver in iati.constants.STANDARD_VERSIONS_SUPPORTED
])
def std_ver_minor_uninst_valid_fullsupport(request):
    """Return an uninstantiated valid minor version number that has full support in pyIATI.

    Todo:
        Add decimal representations where possible.

    """
    return request.param


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS)
def std_ver_minor_inst_valid_known(request):
    """Return an IATI version number that pyIATI knows to exist."""
    return request.param


@pytest.fixture(params=[
    version for version in MINOR_IATIVER_VALID if not iati.Version(version) in iati.constants.STANDARD_VERSIONS
])
def std_ver_minor_inst_valid_unknown(request):
    """Return a version of the IATI Standard that is not known by pyIATI to exist."""
    return iati.Version(request.param)


@pytest.fixture(params=iati.constants.STANDARD_VERSIONS_SUPPORTED)
def std_ver_minor_inst_valid_fullsupport(request):
    """Return a fully supported IATI version number."""
    return request.param


@pytest.fixture(params=[version for version in iati.constants.STANDARD_VERSIONS if version not in iati.constants.STANDARD_VERSIONS_SUPPORTED])
def std_ver_minor_inst_valid_partsupport(request):
    """Return a partially supported IATI version number."""
    return request.param


@pytest.fixture
def std_ver_minor_inst_valid_possible(std_ver_minor_uninst_valid_possible):
    """Return an instantiated IATI Version Number."""
    return iati.Version(std_ver_minor_uninst_valid_possible)


@pytest.fixture
def std_ver_minor_inst_valid_single():
    """Return a single instantiated IATI Version Number."""
    return iati.Version(MINOR_IATIVER_VALID[0])


@pytest.fixture(params=MAJOR_VALID)
def std_ver_major_uninst_valid_possible(request):
    """Return a value that is a correctly formatted representation of a major version number."""
    return request.param

@pytest.fixture(params=MAJOR_INVALID)
def std_ver_major_uninst_valueerr(request):
    """Return a value that looks like it could be a correctly formatted representation of a major version number, but is not."""
    return request.param


@pytest.fixture(params=[
    '1.00', '1.0', '2.0', '2.00',  # integer with a zero decimal
    '1.050',  # valid version with extra 0
    '1.1', '1.2', '1.3', '1.4', '1.5', '2.1', '2.2',  # valid versions with the 0 after the decimal point missing
    '3.0', '3.00', '3.1'  # the first few potential values for the next integer
] + iati.tests.utilities.generate_test_types(['none'], True))  # fuzzing data
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


@pytest.fixture(params=[version for version in iati.constants.STANDARD_VERSIONS if version not in iati.constants.STANDARD_VERSIONS_SUPPORTED])
def standard_version_partial_support(request):
    """Return a version of the IATI Standard that is partially supported by pyIATI."""
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
