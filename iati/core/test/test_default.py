"""A module containing tests for the library representation of default values."""
import iati.core.codelists
import iati.core.default


class TestDefault(object):
    """A container for tests relating to Default data."""

    def test_default_codelists(self):
        """Check that the default Codelists are correct.

        Todo:
            Handle multiple versions.
        """
        codelists = iati.core.default.codelists()

        assert isinstance(codelists, dict)
        assert len(codelists) == 62
        for _, codelist in codelists.items():
            assert isinstance(codelist, iati.core.codelists.Codelist)
