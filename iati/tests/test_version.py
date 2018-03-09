"""A module containing tests for the pyIATI representation of Standard metadata."""
import copy
import math
import operator
import pytest
import iati.tests.utilities
from iati.tests.fixtures.versions import iativer, semver, split_decimal, split_iativer, split_semver


class TestVersionInit(object):
    """A container for tests relating to initialisation of Standard Versions."""

    def test_version_no_params(self):
        """Test Version creation with no parameters."""
        with pytest.raises(TypeError):
            iati.Version()  # pylint: disable=E1120

    def test_version_not_string(self, std_ver_minor_uninst_typeerr):
        """Test Version creation with a non-string."""
        with pytest.raises(TypeError) as excinfo:
            iati.Version(std_ver_minor_uninst_typeerr)

        assert 'A Version object must be created from a string or Decimal, not a ' in str(excinfo.value)
        assert str(type(std_ver_minor_uninst_typeerr)) in str(excinfo.value)

    def test_version_supported_iati_versions(self, std_ver_minor_uninst_valid_fullsupport):
        """Test Version creation with supported IATI version numbers."""
        iati.Version(std_ver_minor_uninst_valid_fullsupport)

    def test_version_valid_decimal(self, std_ver_minor_uninst_valid_decimal_possible):
        """Test Version creations with valid decimal version numbers."""
        integer_component, decimal_component = split_decimal(std_ver_minor_uninst_valid_decimal_possible)

        version = iati.Version(std_ver_minor_uninst_valid_decimal_possible)

        assert version.integer == integer_component
        assert version.major == integer_component
        assert version.decimal == decimal_component
        assert version.minor == decimal_component - 1
        assert version.patch == 0

    def test_version_invalid_float(self, std_ver_minor_uninst_valid_decimal_possible):
        """Test Version creation with a float that would be valid as a Decimal."""
        float_version = float(std_ver_minor_uninst_valid_decimal_possible)

        with pytest.raises(TypeError):
            iati.Version(float_version)

    def test_version_invalid_decimal(self, std_ver_minor_uninst_valueerr_decimal):
        """Test Version creation with a Decimal that is not a valid decimal version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(std_ver_minor_uninst_valueerr_decimal)

        assert str(excinfo.value) == 'A valid version number must be specified.'

    def test_version_valid_iativer(self, std_ver_minor_uninst_valid_iativer_possible):
        """Test Version creations with correctly constructed IATIver version numbers."""
        integer_component, decimal_component = split_iativer(std_ver_minor_uninst_valid_iativer_possible)

        version = iati.Version(std_ver_minor_uninst_valid_iativer_possible)

        assert version.integer == integer_component
        assert version.major == integer_component
        assert version.decimal == decimal_component
        assert version.minor == decimal_component - 1
        assert version.patch == 0

    def test_version_invalid_iativer(self, std_ver_minor_uninst_valueerr_iativer):
        """Test Version creation with a string that is not a valid IATIver version number, but looks like it could be."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(std_ver_minor_uninst_valueerr_iativer)

        assert str(excinfo.value) == 'A valid version number must be specified.'

    def test_version_valid_semver_3_part(self, std_ver_minor_uninst_valid_semver_possible):
        """Test Version creation with valid SemVer version numbers."""
        major_component, minor_component, patch_component = split_semver(std_ver_minor_uninst_valid_semver_possible)

        version = iati.Version(std_ver_minor_uninst_valid_semver_possible)

        assert version.major == major_component
        assert version.integer == major_component
        assert version.minor == minor_component
        assert version.decimal == minor_component + 1
        assert version.patch == patch_component

    def semver_version_invalid_major_0(self, str_ver_minor_uninst_valueerr_v0):
        """Test version creation with a Major version of 0."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(str_ver_minor_uninst_valueerr_v0)

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

        * =: The two values are equal.
        * <: The first value is less than the second.
        * >: The first value is more than the second.
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


class TestVersionModification(object):
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

    def test_attribute_components_writable_valid_values(self, std_ver_minor_inst_valid_possible, modifiable_attrib):
        """Test that the core Version Number Component attributes are writable."""
        attrib_name, idx = modifiable_attrib
        components = split_semver(std_ver_minor_inst_valid_possible.semver_str)
        components[idx] = components[idx] + self.CHANGE_AMOUNT

        version_new = iati.Version(semver(components[0], components[1], components[2]))
        setattr(std_ver_minor_inst_valid_possible, attrib_name, components[idx])

        assert std_ver_minor_inst_valid_possible == version_new

    @pytest.mark.parametrize("not_int", iati.tests.utilities.generate_test_types(['int'], True))
    def test_attribute_components_writable_invalid_values(self, std_ver_minor_inst_valid_single, modifiable_attrib, not_int):
        """Test that core Version Number Components can have invalid values set."""
        attrib_name, _ = modifiable_attrib

        setattr(std_ver_minor_inst_valid_single, attrib_name, not_int)


class TestVersionRepresentation(object):
    """A container for tests relating to how Standard Versions are represented when output."""

    def test_iativer_string_output(self, std_ver_minor_uninst_valid_iativer_possible):
        """Test that the string output for an IATIver version is as expected."""
        integer_component, decimal_component = split_iativer(std_ver_minor_uninst_valid_iativer_possible)
        semver_str = semver(integer_component, decimal_component - 1, 0)

        version = iati.Version(std_ver_minor_uninst_valid_iativer_possible)

        assert str(version) == std_ver_minor_uninst_valid_iativer_possible
        assert repr(version) == "iati.Version('" + semver_str + "')"
        assert version.iativer_str == std_ver_minor_uninst_valid_iativer_possible
        assert version.semver_str == semver_str

    def test_semver_string_output(self, std_ver_minor_uninst_valid_semver_possible):
        """Test that the str() output for an SemVer version is in IATIver-format."""
        major_component, minor_component, _ = split_semver(std_ver_minor_uninst_valid_semver_possible)
        iativer_str = iativer(major_component, minor_component + 1)

        version = iati.Version(std_ver_minor_uninst_valid_semver_possible)

        assert str(version) == iativer_str
        assert repr(version) == "iati.Version('" + std_ver_minor_uninst_valid_semver_possible + "')"
        assert version.iativer_str == iativer_str
        assert version.semver_str == std_ver_minor_uninst_valid_semver_possible


class TestVersionBumping(object):
    """A container for tests relating to bumping of Version Numbers."""

    def test_version_bump_major(self, std_ver_minor_uninst_valid_semver_possible):
        """Test that the next valid Major/Integer version can be located."""
        major_component, _, _ = split_semver(std_ver_minor_uninst_valid_semver_possible)
        next_major_version = iati.Version(semver(major_component + 1, 0, 0))

        version = iati.Version(std_ver_minor_uninst_valid_semver_possible)

        assert isinstance(version.next_major(), iati.Version)
        assert version.next_major() == next_major_version
        assert isinstance(version.next_integer(), iati.Version)
        assert version.next_integer() == next_major_version

    def test_version_bump_minor(self, std_ver_minor_uninst_valid_semver_possible):
        """Test that the next valid Minor/Decimal version can be located."""
        major_component, minor_component, _ = split_semver(std_ver_minor_uninst_valid_semver_possible)
        next_minor_version = iati.Version(semver(major_component, minor_component + 1, 0))

        version = iati.Version(std_ver_minor_uninst_valid_semver_possible)

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

    def test_version_bump_patch(self, std_ver_minor_inst_valid_possible):
        """Test that the next Patch version cannot be obtained."""
        with pytest.raises(AttributeError):
            std_ver_minor_inst_valid_possible.next_patch()

        with pytest.raises(AttributeError):
            std_ver_minor_inst_valid_possible.next_patch  # pylint: disable=pointless-statement

    def test_version_attrib_prerelease(self, std_ver_minor_inst_valid_possible):
        """Test that the 'prerelease' attribute has been set to None on initialisation."""
        assert std_ver_minor_inst_valid_possible.prerelease is None

    def test_version_attrib_build(self, std_ver_minor_inst_valid_possible):
        """Test that the 'build' attribute has been set to None on initialisation."""
        assert std_ver_minor_inst_valid_possible.build is None

    def test_version_attrib_partial(self, std_ver_minor_inst_valid_possible):
        """Test that the 'partial' attribute has been set to True on initialisation."""
        assert std_ver_minor_inst_valid_possible.partial is True


class TestVersionConstants(object):
    """A container for tests relating to constants that define useful groups of IATI version numbers."""

    @pytest.fixture(params=[
        iati.version.STANDARD_VERSIONS,
        iati.version.STANDARD_VERSIONS_SUPPORTED,
        iati.version.STANDARD_VERSIONS_MINOR
    ])
    def standard_versions_list(self, request):
        """Return a list of Version Numbers."""
        return request.param

    def test_standard_versions_all_are_versions(self, standard_versions_list):
        """Check that each item in standard versions is a Version instance."""
        for version in standard_versions_list:
            assert isinstance(version, iati.Version)

    def test_standard_versions_correct_format(self, standard_versions_list):
        """Check that standard versions is in the correct format."""
        assert isinstance(standard_versions_list, list)

    def test_standard_versions_correct_number(self):
        """Check that standard versions has the expected number of items."""
        assert len(iati.version.STANDARD_VERSIONS) == 7

    def test_standard_versions_correct_number_supported(self):
        """Check that supported standard versions has the expected number of items."""
        assert len(iati.version.STANDARD_VERSIONS_SUPPORTED) == 4

    def test_standard_versions_major_all_are_integers(self):
        """Check that each major version is an integer."""
        for major_version in iati.version.STANDARD_VERSIONS_MAJOR:
            assert isinstance(major_version, int)

    def test_standard_versions_major_correct_number(self):
        """Check that the correct number of major versions are detected."""
        assert len(iati.version.STANDARD_VERSIONS_MAJOR) == 2

    def test_standard_versions_minor_correct_number(self):
        """Check that the correct number of minor versions are detected."""
        assert len(iati.version.STANDARD_VERSIONS_MINOR) == 7

    def test_standard_version_any_has_length(self):
        """Check that the value to represent any version is a value with length."""
        assert len(iati.version.STANDARD_VERSION_ANY)


# pylint: disable=protected-access
class VersionSupportChecksBase(object):
    """A container for functions and fixtures used to check version support.

    In their own class to reduce the number of public methods in the parent class below the linting limit of 20.
    """

    @iati.version.allow_fully_supported_version
    def return_fully_supported_version(version):  # pylint: disable=no-self-argument
        """Return the version parameter, but only if it's fully supported by pyIATI. Check undertaken with decorator."""
        return version

    @iati.version.allow_known_version
    def return_known_version(version):  # pylint: disable=no-self-argument
        """Return the version parameter, but only if it's known of by pyIATI. Check undertaken with decorator."""
        return version

    @iati.version.allow_possible_version
    def return_possibly_version(version):  # pylint: disable=no-self-argument
        """Return the version parameter, but only if it's a possible representation of a version number. Check undertaken with decorator."""
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
        return_possibly_version,
        iati.version._prevent_non_version_representations
    ])
    def possibly_version_func(self, request):
        """Return a function that returns a value that represents a possible IATI Version. Other values cause an error."""
        return request.param

    @pytest.fixture(params=[
        iati.version._is_fully_supported,
        iati.version._is_known
    ])
    def truthy_func(self, request):
        """Return a function to check whether an input value is True or False based on whether it's a valid version."""
        return request.param

    @pytest.fixture(params=[
        return_fully_supported_version,
        return_known_version
    ])
    def decorated_func(self, request):
        """Return a function to restrict whether an input value is a valid version, and raise a ValueError if it is not."""
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


class TestVersionSupportChecks(VersionSupportChecksBase):
    """A container for tests relating to the detection of how much pyIATI supports particular versions."""

    def test_fully_supported_version_fully_supported(self, std_ver_minor_inst_valid_fullsupport, decorated_func_full_support):
        """Check that fully supported IATI Versions are detected as such."""
        version = std_ver_minor_inst_valid_fullsupport

        assert iati.version._is_fully_supported(version) is True
        assert decorated_func_full_support(version) == version

    def test_fully_supported_version_partially_supported(self, std_ver_minor_inst_valid_partsupport, decorated_func_full_support):
        """Check that partially supported IATI Versions are detected as not fully supported."""
        assert iati.version._is_fully_supported(std_ver_minor_inst_valid_partsupport) is False

        with pytest.raises(ValueError):
            decorated_func_full_support(std_ver_minor_inst_valid_partsupport)

    def test_known_version_known(self, std_ver_minor_inst_valid_known, decorated_func_known):
        """Check that known IATI Versions are detected as such."""
        assert iati.version._is_known(std_ver_minor_inst_valid_known) is True
        assert decorated_func_known(std_ver_minor_inst_valid_known) == std_ver_minor_inst_valid_known

    def test_known_version_not_known(self, std_ver_minor_inst_valid_unknown, decorated_func_known):
        """Check that unknown IATI Versions are detected as such."""
        assert iati.version._is_known(std_ver_minor_inst_valid_unknown) is False

        with pytest.raises(ValueError):
            decorated_func_known(std_ver_minor_inst_valid_unknown)

    def test_supported_version_str(self, std_ver_minor_uninst_valid_possible, truthy_func, decorated_func):
        """Check that Version Numbers cause an error if provided as anything other than an iati.Version."""
        assert truthy_func(std_ver_minor_uninst_valid_possible) is False

        with pytest.raises(ValueError):
            decorated_func(std_ver_minor_uninst_valid_possible)

    def test_supported_version_junk_value(self, std_ver_minor_uninst_typeerr, truthy_func, decorated_func):
        """Check that supported IATI Versions cause an error if a junk value is provided."""
        assert truthy_func(std_ver_minor_uninst_typeerr) is False

        with pytest.raises(ValueError):
            decorated_func(std_ver_minor_uninst_typeerr)

    def test_non_version_representation_valid_version_obj(self, std_ver_minor_inst_valid_possible, possibly_version_func):
        """Test that instantiated iati.Versions are detected as being valid representations of an IATI Version Number."""
        original_value = copy.deepcopy(std_ver_minor_inst_valid_possible)

        version = possibly_version_func(std_ver_minor_inst_valid_possible)

        assert version == original_value
        assert version is std_ver_minor_inst_valid_possible

    def test_non_version_representation_valid_val_decimal(self, std_ver_minor_uninst_valid_possible, possibly_version_func):
        """Test that values that can become iati.Versions are detected as being valid representations of an IATI Version Number."""
        original_value = copy.deepcopy(std_ver_minor_uninst_valid_possible)

        version = possibly_version_func(std_ver_minor_uninst_valid_possible)

        assert version == original_value
        assert version is std_ver_minor_uninst_valid_possible

    def test_non_version_representation_valid_val_integer(self, std_ver_major_uninst_valid_possible, possibly_version_func):
        """Test that positive integers are detected as being valid representations of an IATI Version Number."""
        original_value = copy.deepcopy(std_ver_major_uninst_valid_possible)

        version = possibly_version_func(std_ver_major_uninst_valid_possible)

        assert version == original_value
        assert version is std_ver_major_uninst_valid_possible

    def test_non_version_representation_valid_val_any(self, possibly_version_func):
        """Test that the specified ANY_VERSION value detected as being valid representations of an IATI Version Number."""
        version = possibly_version_func(iati.version.STANDARD_VERSION_ANY)

        assert version == iati.version.STANDARD_VERSION_ANY

    def test_non_version_representation_invalid_val_integer(self, std_ver_major_uninst_valueerr, possibly_version_func):
        """Test that non-positive integers are detected as not being valid representations of an IATI Version Number."""
        with pytest.raises(ValueError):
            possibly_version_func(std_ver_major_uninst_valueerr)

    def test_non_version_representation_invalid_val(self, std_ver_minor_uninst_valueerr_str_decimal, possibly_version_func):
        """Test that values that are a correct type but cannot be a Decimal Version are detected as a ValueError."""
        with pytest.raises(ValueError):
            possibly_version_func(std_ver_minor_uninst_valueerr_str_decimal)

    def test_non_version_representation_invalid_type(self, std_ver_all_uninst_typeerr, possibly_version_func):
        """Test that values of a type that cannot represent a Version cause a TypeError."""
        with pytest.raises(TypeError):
            possibly_version_func(std_ver_all_uninst_typeerr)


class TestVersionStandardisation(object):
    """A container for tests relating to standardising how versions are passed into functions."""

    @iati.version.decimalise_integer
    def return_decimalised_integer(version):  # pylint: disable=no-self-argument
        """Return the version parameter, but converted to an iati.Version representing the newest Decimal Version in the given Integer Version if something that can be treated as an Integer Version is provided."""
        return version

    @iati.version.normalise_decimals
    def return_normalised_decimal(version):  # pylint: disable=no-self-argument
        """Return the version parameter, but converted to an iati.Version if something that can be treated as a Decimal Version is provided."""
        return version

    INTEGER_TO_DECIMAL_FUNCTIONS = [
        return_decimalised_integer,
        iati.version._decimalise_integer
    ]

    @pytest.fixture(params=INTEGER_TO_DECIMAL_FUNCTIONS)
    def integer_decimalisation_func(self, request):
        """Return a function to check the return value of."""
        return request.param

    DECIMAL_S13N_FUNCTIONS = [
        return_normalised_decimal,
        iati.version._normalise_decimal_version
    ]

    @pytest.fixture(params=DECIMAL_S13N_FUNCTIONS)
    def decimal_normalisation_func(self, request):
        """Return a function to check the return value of."""
        return request.param

    @pytest.fixture(params=INTEGER_TO_DECIMAL_FUNCTIONS + DECIMAL_S13N_FUNCTIONS)
    def junk_ignoring_func(self, request):
        """Return a function that does not modify junk values before returning them."""
        return request.param

    # decimal standardisation
    def test_decimal_versions_normalised(self, std_ver_minor_uninst_valid_possible, decimal_normalisation_func):
        """Check that values that represent Decimal Versions of the IATI Standard are converted to iati.Versions."""
        assert decimal_normalisation_func(std_ver_minor_uninst_valid_possible) == iati.Version(std_ver_minor_uninst_valid_possible)

    def test_integer_versions_not_normalised(self, std_ver_major_uninst_valid_possible, decimal_normalisation_func):
        """Check that values that represent Integer Versions of the IATI Standard are returned as-is when normalising Decimal Versions."""
        assert decimal_normalisation_func(std_ver_major_uninst_valid_possible) == std_ver_major_uninst_valid_possible

    # integer decimalisation
    def test_decimal_version_conversion_valid_version(self, std_ver_minor_inst_valid_known, integer_decimalisation_func):
        """Check that known Decimal Versions remain unchanged."""
        assert integer_decimalisation_func(std_ver_minor_inst_valid_known) == std_ver_minor_inst_valid_known

    def test_decimal_version_conversion_valid_decimal_representation(self, std_ver_minor_uninst_valid_known, integer_decimalisation_func):
        """Check that values that can be used to create actual Decimal Versions are left alone."""
        assert integer_decimalisation_func(std_ver_minor_uninst_valid_known) == std_ver_minor_uninst_valid_known

    @pytest.mark.parametrize('integer_version, expected_decimal', [
        ('1', iati.Version('1.05')),
        ('2', iati.version.STANDARD_VERSION_LATEST),
        ('3', iati.Version('3.0.0'))
    ])
    def test_integer_version_conversion_valid(self, integer_version, expected_decimal, integer_decimalisation_func):
        """Check that valid Integer Versions return the last Decimal in the Integer."""
        assert integer_decimalisation_func(integer_version) == expected_decimal

    def test_junk_values_not_modified(self, std_ver_minor_uninst_mixederr, junk_ignoring_func):
        """Check that junk values are returned as-is when standardising Decimal Versions.

        An `is` check is performed to check that the same object is returned.
        An `==` check is performed to check that the value is not modified.

        """
        try:
            original_value = copy.deepcopy(std_ver_minor_uninst_mixederr)
        except TypeError:
            original_value = std_ver_minor_uninst_mixederr

        result = junk_ignoring_func(std_ver_minor_uninst_mixederr)

        assert result is std_ver_minor_uninst_mixederr
        try:
            assert (result == original_value) or isinstance(original_value, type(iter([]))) or math.isnan(original_value)
        except TypeError:
            # python 2/3 compatibility - identical context managers are not deemed to be equal at Python 2
            import decimal
            import sys
            if not (sys.version_info[0] == 2 and isinstance(original_value, type(decimal.localcontext()))):
                assert False


class TestVersionMajorMinorRelationship(object):
    """A container for tests relating to the relationship between major and minor versions."""

    def test_versions_for_integer(self, std_ver_major_uninst_valid_known):
        """Check that the each of the decimal versions returned by versions_for_integer starts with the input major version."""
        result = iati.version.versions_for_integer(std_ver_major_uninst_valid_known)

        for version in result:
            assert version.major == std_ver_major_uninst_valid_known
