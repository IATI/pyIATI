import pytest

import iati.core.codelists

class TestCodelists(object):
    """A container for tests relating to Codelists"""

    def test_codelist_default_attributes(self):
        """Check a Codelist's default attributes are correct"""
        codelist = iati.core.codelists.Codelist()

        codes = codelist.codes
        name = codelist.name
        path = codelist.path

        assert [] == codes
        assert None == name
        assert None == path

    def test_codelist_name_instance(self):
        """Check a Codelist's attributes are correct when defined with only a name"""
        name_to_set = "test Codelist name"
        codelist = iati.core.codelists.Codelist(name_to_set)

        codes = codelist.codes
        name = codelist.name
        path = codelist.path

        assert [] == codes
        assert name_to_set == name
        assert None == path


class TestCodes(object):
    """A container for tests relating to Codes"""

    def test_code_default_attributes(self):
        """Check a Code's default attributes are correct"""
        code = iati.core.codelists.Code()

        name = code.name
        value = code.value

        assert None == name
        assert None == value

    def test_code_value_instance(self):
        """Check a Code's attributes are correct when being defined with only a value"""
        value_to_set = "test Code value"
        code = iati.core.codelists.Code(value_to_set)

        name = code.name
        value = code.value

        assert None == name
        assert value_to_set == value

    def test_code_value_and_name_instance(self):
        """Check a Code's attributes are correct when being defined with a value and name"""
        value_to_set = "test Code value"
        name_to_set = "test Code name"
        code = iati.core.codelists.Code(value_to_set, name_to_set)

        name = code.name
        value = code.value

        assert name_to_set == name
        assert value_to_set == value
