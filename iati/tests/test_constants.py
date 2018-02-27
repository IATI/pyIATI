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
