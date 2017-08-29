"""A module containing tests for the library representation of IATI constants."""
import iati.core.constants


class TestConstants(object):
    """A container for tests relating to IATI software constants."""

    def test_namespace(self):
        """Check that the NAMESPACE constant is a string."""
        assert isinstance(iati.core.constants.NAMESPACE, str)

    def test_nsmap(self):
        """Check that the NSMAP constant is a dictionary with the correct key."""
        assert isinstance(iati.core.constants.NSMAP, dict)
        assert isinstance(iati.core.constants.NSMAP['xsd'], str)

    def test_standard_versions_all_are_numbers(self):
        """Check that each item in standard versions is a string that can be converted to a float."""
        for version in iati.core.constants.STANDARD_VERSIONS:
            assert isinstance(version, str)
            assert float(version)

    def test_standard_versions_correct_format(self):
        """Check that standard versions is in the correct format."""
        assert isinstance(iati.core.constants.STANDARD_VERSIONS, list)

    def test_standard_versions_correct_number(self):
        """Check that standard versions has the expected number of items."""
        assert len(iati.core.constants.STANDARD_VERSIONS) == 4
