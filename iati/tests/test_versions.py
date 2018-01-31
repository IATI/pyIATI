"""A module containing tests for the pyIATI representation of Standard metadata."""
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

    @pytest.fixture(params=[
        iativer(components[0], components[1]) for components in
        list(itertools.product(ONE_TO_LOTS, ONE_TO_NINE)) +  # decimals from 1-9 inclusive
        list(itertools.product(TWO_TO_LOTS, TEN_TO_LOTS))  # decimals from 10-up for integers from 2 up
    ])
    def iativer_version_valid(self, request):
        """Return a valid IATIver-format version number."""
        return request.param

    @pytest.fixture(params=[
        iativer(components[0], components[1]) for components in
        list(itertools.product([1], TEN_TO_LOTS)) +  # integer 1 may only decimal 01-09
        list(itertools.product([0], ONE_TO_NINE + TEN_TO_LOTS)) +  # integer value of 0
        list(itertools.product(ONE_TO_LOTS, [0])) +  # decimal value of 0
        list(itertools.product(NEGATIVE_NUMBERS, ONE_TO_NINE)) +  # negative integer
        list(itertools.product(ONE_TO_LOTS, NEGATIVE_NUMBERS))  # negative decimal
    ] + [
        str(components[0]) + '.' + str(components[1]) for components in itertools.product(ONE_TO_LOTS, ONE_TO_NINE)  # non-padded Decimal
    ])
    def iativer_version_invalid(self, request):
        """Return an version number that looks like it could be an IATIver-format version, but isn't."""
        return request.param

    @pytest.fixture(params=generate_semver_list(ONE_TO_LOTS, ZERO_TO_LOTS, ZERO_TO_LOTS))
    def semver_3_part_valid(self, request):
        """Return a valid 3-part SemVer-format version number."""
        return request.param


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

        assert 'A Version object must be created from a string, not a ' in str(excinfo.value)
        assert str(type(not_str)) in str(excinfo.value)

    def test_version_supported_iati_versions(self, standard_version_mandatory):
        """Test Version creation with supported IATI version numbers."""
        iati.Version(*standard_version_mandatory)

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


class TestVersionImplementationDetailHiding(object):
    """A container for tests relating to ensuring implementation detail is hidden.

    The implementation of the Version class makes use of a Semantic Versioning library by inheriting from a base class.
    The utilised base class contains attributes that are not desired.
    Tests in this container check that attributes that are not desired have been hidden.
    """

    def test_version_bump_patch(self):
        """Test that the next Patch version cannot be obtained."""
        version = iati.Version('1.0.0')

        with pytest.raises(AttributeError):
            version.next_patch()

        with pytest.raises(AttributeError):
            version.next_patch
