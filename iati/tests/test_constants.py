"""A module containing tests for the library representation of IATI constants."""
import pytest
import iati.constants


class TestConstants(object):
    """A container for tests relating to IATI software constants."""

    @pytest.fixture(params=[
        iati.constants.STANDARD_VERSIONS,
        iati.constants.STANDARD_VERSIONS_SUPPORTED,
        iati.constants.STANDARD_VERSIONS_MINOR
    ])
    def standard_versions_list(self, request):
        """Return a list of Version Numbers."""
        return request.param

    def test_namespace(self):
        """Check that the NAMESPACE constant is a string."""
        assert isinstance(iati.constants.NAMESPACE, str)

    def test_nsmap(self):
        """Check that the NSMAP constant is a dictionary with the correct key."""
        assert isinstance(iati.constants.NSMAP, dict)
        assert isinstance(iati.constants.NSMAP['xsd'], str)

    def test_standard_versions_all_are_numbers(self, standard_versions_list):
        """Check that each item in standard versions is a string that can be considered to be a correctly formatted decimal number."""
        for version in standard_versions_list:
            split_version = version.split('.')

            assert isinstance(version, str)
            assert float(version)
            assert len(split_version) == 2
            assert len(split_version[1]) == 2
            assert version == version.strip()

    def test_standard_versions_correct_format(self, standard_versions_list):
        """Check that standard versions is in the correct format."""
        assert isinstance(standard_versions_list, list)

    def test_standard_versions_correct_number(self):
        """Check that standard versions has the expected number of items."""
        assert len(iati.constants.STANDARD_VERSIONS) == 7

    def test_standard_versions_correct_number_supported(self):
        """Check that supported standard versions has the expected number of items."""
        assert len(iati.constants.STANDARD_VERSIONS_SUPPORTED) == 4

    def test_standard_versions_major_all_are_integers(self):
        """Check that each major version is an integer."""
        for major_version in iati.constants.STANDARD_VERSIONS_MAJOR:
            assert isinstance(major_version, int)

    def test_standard_versions_major_correct_number(self):
        """Check that the correct number of major versions are detected."""
        assert len(iati.constants.STANDARD_VERSIONS_MAJOR) == 2

    def test_standard_versions_minor_correct_number(self):
        """Check that the correct number of minor versions are detected."""
        assert len(iati.constants.STANDARD_VERSIONS_MINOR) == 7
