import pytest

import iati.core.constants

class TestConstants(object):
    """A containter for tests relating to IATI software constants"""

    def test_nsmap(self):
        """Check that the NSMAP constant exists"""
        assert None != iati.core.constants.NSMAP
