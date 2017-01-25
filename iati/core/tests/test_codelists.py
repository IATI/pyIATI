"""
A module containing tests for the library representation of Codelists.
"""

import iati.core.codelists


class TestCodelists(object):
    """A container for tests relating to Codelists"""

    def test_codelist_default_attributes(self):
        """Check a Codelist's default attributes are correct"""
        codelist = iati.core.codelists.Codelist()

        assert [] == codelist.codes
        assert codelist.name is None
        assert codelist.path is None

    def test_codelist_name_instance(self):
        """Check a Codelist's attributes are correct when defined with only a name"""
        name_to_set = "test Codelist name"
        codelist = iati.core.codelists.Codelist(name_to_set)

        assert [] == codelist.codes
        assert codelist.name == name_to_set
        assert codelist.path is None

    def test_codelist_name_and_path_instance(self):
        """Check a Codelist's attributes are correct when defined with a name and path"""
        name_to_set = "test Codelist name"
        path_to_set = "test Codelist path"
        codelist = iati.core.codelists.Codelist(name_to_set, path_to_set)

        assert [] == codelist.codes
        assert codelist.name == name_to_set
        assert codelist.path == path_to_set

    def test_codelist_add_code(self):
        """Check a Code can be added to a Codelist"""
        codelist = iati.core.codelists.Codelist()
        code = iati.core.codelists.Code()
        codelist.add_code(code)

        num_codes = len(codelist.codes)

        assert num_codes == 1

    def test_codelist_add_code_decline_non_code(self):
        """Check something that is not a Code cannot be added to a Codelist"""
        codelist = iati.core.codelists.Codelist()
        not_a_code = True
        codelist.add_code(not_a_code)

        num_codes = len(codelist.codes)

        assert num_codes == 0

    def test_codelist_define_from_xml(self):
        """Check that a Codelist can be generated from an XML codelist definition"""
        path = iati.core.resources.path_codelist('FlowType')
        xml_str = iati.core.resources.load_as_string(path)
        codelist = iati.core.codelists.Codelist(xml=xml_str)

        assert codelist.name == 'FlowType'
        assert len(codelist.codes) == 6
        assert codelist.codes[0].value == '10'


class TestCodes(object):
    """A container for tests relating to Codes"""

    def test_code_default_attributes(self):
        """Check a Code's default attributes are correct"""
        code = iati.core.codelists.Code()

        assert code.name is None
        assert code.value is None

    def test_code_value_instance(self):
        """Check a Code's attributes are correct when being defined with only a value"""
        value_to_set = "test Code value"
        code = iati.core.codelists.Code(value_to_set)

        assert code.name is None
        assert code.value == value_to_set

    def test_code_value_and_name_instance(self):
        """Check a Code's attributes are correct when being defined with a value and name"""
        value_to_set = "test Code value"
        name_to_set = "test Code name"
        code = iati.core.codelists.Code(value_to_set, name_to_set)

        assert code.name == name_to_set
        assert code.value == value_to_set
