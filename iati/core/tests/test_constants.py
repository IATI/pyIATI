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
