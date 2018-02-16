"""A module containing tests for the library representation of IATI constants."""
import iati.constants


class TestConstants(object):
    """A container for tests relating to IATI software constants."""

    def test_namespace(self):
        """Check that the NAMESPACE constant is a string."""
        assert isinstance(iati.constants.NAMESPACE, str)

    def test_nsmap(self):
        """Check that the NSMAP constant is a dictionary with the correct key."""
        assert isinstance(iati.constants.NSMAP, dict)
        assert isinstance(iati.constants.NSMAP['xsd'], str)

    def test_standard_versions_all_are_numbers(self):
        """Check that each item in standard versions is a string that can be considered to be a decimal number."""
        for version in iati.constants.STANDARD_VERSIONS:
            assert isinstance(version, str)
            assert float(version)

    def test_standard_versions_correct_format(self):
        """Check that standard versions is in the correct format."""
        assert isinstance(iati.constants.STANDARD_VERSIONS, list)

    def test_standard_versions_correct_number(self):
        """Check that standard versions has the expected number of items."""
        assert len(iati.constants.STANDARD_VERSIONS) == 5

    def test_standard_versions_major_all_are_integers(self):
        """Check that each major version is an integer."""
        for major_version in iati.constants.STANDARD_VERSIONS_MAJOR:
            assert isinstance(major_version, int)

    def test_standard_versions_major_correct_number(self):
        """Check that the correct number of major versions are detected."""
        assert len(iati.constants.STANDARD_VERSIONS_MAJOR) == 2
