"""A module containing tests for the pyIATI representation of Standard metadata."""
import pytest
import iati.tests.utilities


class TestVersions(object):
    """A container for tests relating to Standard Versions."""

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

    def test_version_valid_iati_versions(self, standard_version_mandatory):
        """Test Version creations with IATI version numbers."""
        _ = iati.Version(*standard_version_mandatory)
