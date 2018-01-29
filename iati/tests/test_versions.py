"""A module containing tests for the pyIATI representation of Standard metadata."""
import itertools
import pytest
import iati.tests.utilities


class TestVersions(object):
    """A container for tests relating to Standard Versions."""

    @pytest.fixture(params=[str(components[0]) + '.' + str(components[1]).zfill(2) for components in itertools.product(range(1, 1100, 51), range(1, 10))])
    def standard_version_valid(self, request):
        """Return a valid IATI version number."""
        return request.param

    @pytest.fixture(params=[
        str(components[0]) + '.' + str(components[1]).zfill(2) for components in
            list(itertools.product(range(1, 1100, 51), range(10, 1000, 51))) +  # invalid Decimal
            list(itertools.product([0], range(1, 10))) +  # integer value of 0
            list(itertools.product(range(1, 1100, 51), [0])) +  # decimal value of 0
            list(itertools.product(range(-10, 0), range(1, 10)))  # negative integer
    ] +
    [
        str(components[0]) + '.' + str(components[1]) for components in itertools.product(range(1, 1100, 51), range(1, 10))  # non-padded Decimal
    ])
    def standard_version_invalid(self, request):
        """Return an invalid IATI version number."""
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
        _ = iati.Version(*standard_version_mandatory)

    def test_version_valid_iati_versions(self, standard_version_valid):
        """Test Version creations with correctly constructed IATI version numbers."""
        _ = iati.Version(standard_version_valid)

    def test_version_invalid(self, standard_version_invalid):
        """Test Version creation with a string that is not a valid version number."""
        with pytest.raises(ValueError) as excinfo:
            iati.Version(standard_version_invalid)

        assert str(excinfo.value) == 'A valid version number must be specified.'
