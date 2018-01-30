"""A module containing tests for the pyIATI representation of Standard metadata."""
import itertools
import pytest
import iati.tests.utilities


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


class TestVersions(object):
    """A container for tests relating to Standard Versions."""

    @pytest.fixture(params=[
        str(components[0]) + '.0' + str(components[1]) for components in
        list(itertools.product(ONE_TO_LOTS, ONE_TO_NINE)) +  # decimals from 1-9 inclusive
        list(itertools.product(TWO_TO_LOTS, TEN_TO_LOTS))  # decimals from 10-up for integers from 2 up
    ])
    def iativer_version_valid(self, request):
        """Return a valid IATIver-format version number."""
        return request.param

    @pytest.fixture(params=[
        str(components[0]) + '.0' + str(components[1]) for components in
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
        """Test Version creations with supported IATI version numbers."""
        iati.Version(*standard_version_mandatory)

    def test_version_valid_iativer(self, iativer_version_valid):
        """Test Version creations with correctly constructed IATIver version numbers."""
        iati.Version(iativer_version_valid)

    def test_version_invalid_iativer(self, iativer_version_invalid):
        """Test Version creation with a string that is not a valid IATIver version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(iativer_version_invalid)

        assert str(excinfo.value) == 'A valid version number must be specified.'
