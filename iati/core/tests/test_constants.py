"""A module containing tests for the library representation of IATI constants."""
import iati.core.constants


class TestConstants(object):
    """A container for tests relating to IATI software constants"""

    def test_nsmap(self):
        """Check that the NSMAP constant exists

        Todo:
            Check that NSMAP is a sensible value.
        """
        assert iati.core.constants.NSMAP is not None
