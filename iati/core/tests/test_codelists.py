import pytest

import iati.core.codelists

class TestCodelists(object):
    """A container for tests relating to Codelists"""

    def test_codelist_default_attributes(self):
        """Check a Codelist's default attributes are correct"""
        codelist = iati.core.codelists.Codelist()

        codes = codelist.codes
        condition = codelist.condition
        name = codelist.name
        path = codelist.path

        assert codes == []
        assert condition == None
        assert name == None
        assert path == None

class TestCodes(object):
    """A container for tests relating to Codes"""

    def test_code_default_attributes(self):
        """Check a Code's default attributes are correct"""
        code = iati.core.codelists.Code()

        activation_date = code.activation_date
        name = code.name
        value = code.value

        assert activation_date == None
        assert name == None
        assert value == None
