import pytest

import iati.core.codelists

class TestCodelists(object):
    """A container for tests relating to codelists"""
    pass

class TestCodes(object):
    """A container for tests relating to codes"""

    def test_code_default_activation_date(self):
        """Check a Code's default activation date is correct"""
        code = iati.core.codelists.Code()

        result = code.activation_date

        assert result == None
