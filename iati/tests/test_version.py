"""A module containing tests for the pyIATI representation of Standard metadata."""
from decimal import Decimal
import itertools
import operator
import pytest
import iati.tests.utilities


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


class VersionNumberTestBase(object):
    """A container for fixtures that generate Version Numbers."""

    DECIMAL_VALID = [
        Decimal('1.0' + str(minor)) for minor in ONE_TO_NINE  # base permitted values
    ] + [
        Decimal('1.010')  # equivalent to `Decimal('1.01')`
    ]
    """list of Decimal: A list of valid Decimal version numbers."""

    DECIMAL_INVALID = [
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

    IATIVER_VALID = [
        iativer(components[0], components[1]) for components in
        list(itertools.product(ONE_TO_LOTS, ONE_TO_NINE)) +  # decimals from 1-9 inclusive
        list(itertools.product(TWO_TO_LOTS, TEN_TO_LOTS))  # decimals from 10-up for integers from 2 up
    ]
    """list of str: A list of valid IATIver format version numbers."""

    SEMVER_VALID = generate_semver_list(ONE_TO_LOTS, ZERO_TO_LOTS, ZERO_TO_LOTS)
    """list of str: A list of valid SemVer format version numbers."""

    MIXED_VER_VALID = IATIVER_VALID + SEMVER_VALID
    """list of str: A list of valid version numbers of any permitted format."""

    @pytest.fixture(params=DECIMAL_VALID)
    def decimal_version_valid(self, request):
        """Return a valid decimal version number."""
        return request.param

    @pytest.fixture(params=DECIMAL_INVALID)
    def decimal_version_invalid(self, request):
        """Return an invalid decimal version number."""
        return request.param

    @pytest.fixture(params=IATIVER_VALID)
    def iativer_version_valid(self, request):
        """Return a valid IATIver-format version number."""
        return request.param

    @pytest.fixture(params=[
        iativer(components[0], components[1]) for components in  # pylint: disable=undefined-loop-variable
        list(itertools.product([1], TEN_TO_LOTS)) +  # integer 1 may only decimal 01-09
        list(itertools.product([0], ONE_TO_NINE + TEN_TO_LOTS)) +  # integer value of 0
        list(itertools.product(ONE_TO_LOTS, [0])) +  # decimal value of 0
        list(itertools.product(NEGATIVE_NUMBERS, ONE_TO_NINE)) +  # negative integer
        list(itertools.product(ONE_TO_LOTS, NEGATIVE_NUMBERS))  # negative decimal
    ] + [
        str(components[0]) + '.' + str(components[1]) for components in itertools.product(ONE_TO_LOTS, ONE_TO_NINE)  # non-padded Decimal  # pylint: disable=undefined-loop-variable
    ])
    def iativer_version_invalid(self, request):
        """Return an version number that looks like it could be an IATIver-format version, but isn't."""
        return request.param

    @pytest.fixture(params=SEMVER_VALID)
    def semver_3_part_valid(self, request):
        """Return a valid 3-part SemVer-format version number."""
        return request.param

    @pytest.fixture(params=MIXED_VER_VALID)
    def mixed_ver_format_valid(self, request):
        """Return a valid version number in a valid format."""
        return request.param

    @pytest.fixture
    def version(self, mixed_ver_format_valid):
        """Return an instantiated IATI Version Number."""
        return iati.Version(mixed_ver_format_valid)

    @pytest.fixture
    def single_version(self):
        """Return a single instantiated IATI Version Number."""
        return iati.Version('1.2.3')


class TestVersionInit(VersionNumberTestBase):
    """A container for tests relating to initialisation of Standard Versions."""

    def test_version_no_params(self):
        """Test Version creation with no parameters."""
        with pytest.raises(TypeError):
            iati.Version()  # pylint: disable=E1120

    @pytest.mark.parametrize("not_version_str", [
        '',  # empty string
        ' ',  # whitespace
        'not a version',  # letters
        ':)',  # symbols
        '.',  # only a separator
        '+'  # only a build number separator
    ])
    def test_version_invalid_string(self, not_version_str):
        """Test Version creation with a string that is not a version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(not_version_str)

        assert str(excinfo.value) == 'A valid version number must be specified.'

    @pytest.mark.parametrize("not_str", iati.tests.utilities.generate_test_types(['str'], True))
    def test_version_not_string(self, not_str):
        """Test Version creation with a non-string."""
        with pytest.raises(TypeError) as excinfo:
            iati.Version(not_str)

        assert 'A Version object must be created from a string or Decimal, not a ' in str(excinfo.value)
        assert str(type(not_str)) in str(excinfo.value)

    def test_version_supported_iati_versions(self, standard_version_mandatory):
        """Test Version creation with supported IATI version numbers."""
        iati.Version(standard_version_mandatory[0].iativer_str)

    def test_version_valid_decimal(self, decimal_version_valid):
        """Test Version creations with valid decimal version numbers."""
        integer_component, decimal_component = split_decimal(decimal_version_valid)

        version = iati.Version(decimal_version_valid)

        assert version.integer == integer_component
        assert version.major == integer_component
        assert version.decimal == decimal_component
        assert version.minor == decimal_component - 1
        assert version.patch == 0

    def test_version_invalid_float(self, decimal_version_valid):
        """Test Version creation with a float that would be valid as a Decimal."""
        float_version = float(decimal_version_valid)

        with pytest.raises(TypeError):
            iati.Version(float_version)

    def test_version_invalid_decimal(self, decimal_version_invalid):
        """Test Version creation with a Decimal that is not a valid decimal version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(decimal_version_invalid)

        assert str(excinfo.value) == 'A valid version number must be specified.'

    def test_version_valid_iativer(self, iativer_version_valid):
        """Test Version creations with correctly constructed IATIver version numbers."""
        integer_component, decimal_component = split_iativer(iativer_version_valid)

        version = iati.Version(iativer_version_valid)

        assert version.integer == integer_component
        assert version.major == integer_component
        assert version.decimal == decimal_component
        assert version.minor == decimal_component - 1
        assert version.patch == 0

    def test_version_invalid_iativer(self, iativer_version_invalid):
        """Test Version creation with a string that is not a valid IATIver version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(iativer_version_invalid)

        assert str(excinfo.value) == 'A valid version number must be specified.'

    def test_version_valid_semver_3_part(self, semver_3_part_valid):
        """Test Version creation with valid SemVer version numbers."""
        major_component, minor_component, patch_component = split_semver(semver_3_part_valid)

        version = iati.Version(semver_3_part_valid)

        assert version.major == major_component
        assert version.integer == major_component
        assert version.minor == minor_component
        assert version.decimal == minor_component + 1
        assert version.patch == patch_component

    @pytest.mark.parametrize('version_str', generate_semver_list([0], ZERO_TO_LOTS, ZERO_TO_LOTS))
    def semver_version_invalid_major_0(self, version_str):
        """Test version creation with a Major version of 0."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(version_str)

        assert str(excinfo.value) == 'A valid version number must be specified.'


class TestVersionComparison(object):
    """A container for tests relating to comparison between Standard Versions."""

    @pytest.fixture(params=[
        # with patch components of zero
        ('1.01', '1.01', '='),  # equal IATIver - zero minor
        ('1.0.0', '1.0.0', '='),  # equal SemVer - zero minor
        ('1.01', '1.0.0', '='),  # equal IATIver and SemVer - zero minor
        ('1.0.0', '1.01', '='),  # equal Semver and IATIVer - zero minor
        ('1.02', '1.02', '='),  # equal IATIver - non-zero minor
        ('1.1.0', '1.1.0', '='),  # equal SemVer - non-zero minor
        ('1.02', '1.1.0', '='),  # equal IATIver and SemVer - non-zero minor
        ('1.1.0', '1.02', '='),  # equal SemVer and IATIver - non-zero minor
        ('1.01', '1.02', '<'),  # less than IATIver - minor
        ('1.0.0', '1.1.0', '<'),  # less than SemVer - minor
        ('1.01', '1.1.0', '<'),  # less than IATIver and SemVer - minor
        ('1.0.0', '1.02', '<'),  # less than SemVer and IATIver - minor
        ('1.01', '2.01', '<'),  # less than IATIver - major
        ('1.0.0', '2.0.0', '<'),  # less than SemVer - major
        ('1.01', '2.0.0', '<'),  # less than IATIver and SemVer - major
        ('1.0.0', '2.01', '<'),  # less than SemVer and IATIVer - major
        ('1.1.0', '1.0.0', '>'),  # more than SemVer - minor
        ('1.1.0', '1.01', '>'),  # more than IATIver and SemVer - minor
        ('1.02', '1.0.0', '>'),  # more than SemVer and IATIver - minor
        ('2.01', '1.01', '>'),  # more than IATIver - major
        ('2.0.0', '1.0.0', '>'),  # more than SemVer - major
        ('2.01', '1.0.0', '>'),  # more than IATIver and SemVer - major
        ('2.0.0', '1.01', '>'),  # more than SemVer and IATIVer - major
        # non-zero patch components
        ('1.02', '1.1.7', '<'),  # less than IATIver and SemVer - different patch
        ('1.1.7', '1.02', '>'),  # more equal SemVer and IATIver - different patch
        ('1.1.6', '1.1.7', '<'),  # less than SemVer - patch
        ('1.1.7', '1.1.6', '>')  # more than SemVer - patch
    ])
    def version_relationship(self, request):
        """Return a tuple containing a pair of Version Numbers and their relationships.

        The first two items in the tuple are Version Numbers.
        The third item is a string containing symbols indicating the relationship.
            '=': The two values are equal.
            '<': The first value is less than the second.
            '>': The first value is more than the second.
        """
        return request.param

    @pytest.fixture(params=[
        (operator.eq, ['=']),
        (operator.ne, ['<', '>']),
        (operator.lt, ['<']),
        (operator.le, ['<', '=']),
        (operator.gt, ['>']),
        (operator.ge, ['>', '='])
    ])
    def comparison_op_mapping(self, request):
        """Return a tuple containing a comparison operator and a list of symbols it represents."""
        return request.param

    def test_comparisons(self, version_relationship, comparison_op_mapping):
        """Test that the relationships between two Versions are correctly detected."""
        version_1 = iati.Version(version_relationship[0])
        version_2 = iati.Version(version_relationship[1])
        expected_relationships = version_relationship[2]
        comparison_op, op_relationships = comparison_op_mapping

        should_pass = len([op for op in op_relationships if op in expected_relationships]) > 0
        result = comparison_op(version_1, version_2)

        assert result == should_pass


class TestVersionModification(VersionNumberTestBase):
    """A container for tests relating to modifying Version Numbers after they are instantiated."""

    CHANGE_AMOUNT = 10
    """int: The amount that Components are modified by."""

    @pytest.fixture(params=[
        ('major', 0),
        ('integer', 0),
        ('minor', 1),
        ('decimal', 1),
        ('patch', 2)
    ])
    def modifiable_attrib(self, request):
        """Return a tuple containing the name of a component within a Version, plus the index it appears when components are ordered from most to least major."""
        return request.param

    def test_attribute_components_writable_valid_values(self, version, modifiable_attrib):
        """Test that the core Version Number Component attributes are writable."""
        attrib_name, idx = modifiable_attrib
        components = split_semver(version.semver_str)
        components[idx] = components[idx] + self.CHANGE_AMOUNT

        version_new = iati.Version(semver(components[0], components[1], components[2]))
        setattr(version, attrib_name, components[idx])

        assert version == version_new

    @pytest.mark.parametrize("not_int", iati.tests.utilities.generate_test_types(['int'], True))
    def test_attribute_components_writable_invalid_values(self, single_version, modifiable_attrib, not_int):
        """Test that core Version Number Components can have invalid values set."""
        attrib_name, _ = modifiable_attrib

        setattr(single_version, attrib_name, not_int)


class TestVersionRepresentation(VersionNumberTestBase):
    """A container for tests relating to how Standard Versions are represented when output."""

    def test_iativer_string_output(self, iativer_version_valid):
        """Test that the string output for an IATIver version is as expected."""
        integer_component, decimal_component = split_iativer(iativer_version_valid)
        semver_str = semver(integer_component, decimal_component - 1, 0)

        version = iati.Version(iativer_version_valid)

        assert str(version) == iativer_version_valid
        assert repr(version) == "iati.Version('" + semver_str + "')"
        assert version.iativer_str == iativer_version_valid
        assert version.semver_str == semver_str

    def test_semver_string_output(self, semver_3_part_valid):
        """Test that the str() output for an SemVer version is in IATIver-format."""
        major_component, minor_component, _ = split_semver(semver_3_part_valid)
        iativer_str = iativer(major_component, minor_component + 1)

        version = iati.Version(semver_3_part_valid)

        assert str(version) == iativer_str
        assert repr(version) == "iati.Version('" + semver_3_part_valid + "')"
        assert version.iativer_str == iativer_str
        assert version.semver_str == semver_3_part_valid


class TestVersionBumping(VersionNumberTestBase):
    """A container for tests relating to bumping of Version Numbers."""

    def test_version_bump_major(self, semver_3_part_valid):
        """Test that the next valid Major/Integer version can be located."""
        major_component, _, _ = split_semver(semver_3_part_valid)
        next_major_version = iati.Version(semver(major_component + 1, 0, 0))

        version = iati.Version(semver_3_part_valid)

        assert isinstance(version.next_major(), iati.Version)
        assert version.next_major() == next_major_version
        assert isinstance(version.next_integer(), iati.Version)
        assert version.next_integer() == next_major_version

    def test_version_bump_minor(self, semver_3_part_valid):
        """Test that the next valid Minor/Decimal version can be located."""
        major_component, minor_component, _ = split_semver(semver_3_part_valid)
        next_minor_version = iati.Version(semver(major_component, minor_component + 1, 0))

        version = iati.Version(semver_3_part_valid)

        assert isinstance(version.next_minor(), iati.Version)
        assert version.next_minor() == next_minor_version
        assert isinstance(version.next_decimal(), iati.Version)
        assert version.next_decimal() == next_minor_version


class TestVersionImplementationDetailHiding(VersionNumberTestBase):
    """A container for tests relating to ensuring implementation detail is hidden.

    The implementation of the Version class makes use of a Semantic Versioning library by inheriting from a base class.
    The utilised base class contains attributes that are not desired.
    Tests in this container check that attributes that are not desired have been hidden.
    """

    def test_version_bump_patch(self, version):
        """Test that the next Patch version cannot be obtained."""
        with pytest.raises(AttributeError):
            version.next_patch()

        with pytest.raises(AttributeError):
            version.next_patch  # pylint: disable=pointless-statement

    def test_version_attrib_prerelease(self, version):
        """Test that the 'prerelease' attribute has been set to None on initialisation."""
        assert version.prerelease is None

    def test_version_attrib_build(self, version):
        """Test that the 'build' attribute has been set to None on initialisation."""
        assert version.build is None

    def test_version_attrib_partial(self, version):
        """Test that the 'partial' attribute has been set to True on initialisation."""
        assert version.partial is True


# pylint: disable=protected-access
class TestVersionRounding(object):
    """A container for tests relating to rounding versions to various levels of specificity."""

    @iati.version.convert_to_decimal
    def return_decimalised_version(version):
        """Return the version parameter, converted to the latest Decimal through use of a decorator."""
        return version

    @pytest.fixture(params=[
        return_decimalised_version,
        iati.version._specific_version_for
    ])
    def func_to_test(self, request):
        """Return a function to check the return value of."""
        return request.param

    def test_decimal_version_conversion_valid(self, standard_version_all, func_to_test):
        """Check that Decimal Versions remain unchanged."""
        assert func_to_test(standard_version_all) == standard_version_all

    @pytest.mark.parametrize('integer_version, expected_decimal', [
        ('1', iati.Version('1.05')),
        ('2', iati.constants.STANDARD_VERSION_LATEST),
        ('3', iati.Version('3.0.0'))
    ])
    def test_integer_version_conversion_valid(self, integer_version, expected_decimal, func_to_test):
        """Check that valid Integer Versions return the last Decimal in the Integer."""
        assert func_to_test(integer_version) == expected_decimal

    def test_version_conversion_invalid(self, std_version_invalid, func_to_test):
        """Check that invalid versions cause a ValueError."""
        with pytest.raises(ValueError):
            func_to_test(std_version_invalid)

    def test_version_conversion_None(self, func_to_test):
        """Check that None cause a ValueError."""
        with pytest.raises(ValueError):
            func_to_test(None)


# pylint: disable=protected-access
class TestVersionSupportChecks(VersionNumberTestBase):
    """A container for tests relating to the detection of how much pyIATI supports particular versions."""

    @iati.version.fully_supported_version
    def return_fully_supported_version(version):
        """Return the version parameter, but only if it's fully supported by pyIATI. Check undertaken with decorator."""
        return version

    @iati.version.known_version
    def return_known_version(version):
        """Return the version parameter, but only if it's known of by pyIATI. Check undertaken with decorator."""
        return version

    @pytest.fixture(params=[return_fully_supported_version])
    def decorated_func_full_support(self, request):
        """Return a decorated function that returns a version of the IATI Standard that is fully supported by pyIATI."""
        return request.param

    @pytest.fixture(params=[return_known_version])
    def decorated_func_known(self, request):
        """Return a decorated function that returns a version of the IATI Standard that pyIATI knows exists."""
        return request.param

    @pytest.fixture(params=[
        return_fully_supported_version,
        iati.version._is_fully_supported,
        return_known_version,
        iati.version._is_known
    ])
    def func_to_test(self, request):
        """Return a function to check for TypeErrors being raised when provided values other than iati.Versions."""
        return request.param

    def test_fully_supported_version_fully_supported(self, standard_version_mandatory, decorated_func_full_support):
        """Check that fully supported IATI Versions are detected as such."""
        version = standard_version_mandatory[0]

        assert iati.version._is_fully_supported(version) == True
        assert decorated_func_full_support(version) == version

    def test_fully_supported_version_partially_supported(self, standard_version_partial_support, decorated_func_full_support):
        """Check that partially supported IATI Versions are detected as not fully supported."""
        assert iati.version._is_fully_supported(standard_version_partial_support) == False

        with pytest.raises(ValueError):
            decorated_func_full_support(standard_version_partial_support)

    def test_fully_supported_version_known(self, standard_version_all, decorated_func_known):
        """Check that fully supported IATI Versions are detected as such."""
        assert iati.version._is_known(standard_version_all) == True
        assert decorated_func_known(standard_version_all) == standard_version_all

    def test_supported_version_str(self, standard_version_mandatory, func_to_test):
        """Check that Version Numbers cause an error if provided as a string."""
        with pytest.raises(TypeError):
            func_to_test(str(*standard_version_mandatory))

    @pytest.mark.parametrize('not_a_version', iati.tests.utilities.generate_test_types([], True))
    def test_supported_version_junk_value(self, not_a_version, func_to_test):
        """Check that fully supported IATI Versions cause an error if a junk value is provided."""
        with pytest.raises(TypeError):
            func_to_test(not_a_version)
