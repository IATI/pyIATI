"""A module containing tests for the library representation of Codelists."""
import pytest
from lxml import etree
import iati.core.codelists


class TestCodelistsNonClass(object):
    """Test codelists functionality that is not contained within a class."""

    def test_mappings(self):
        """Check that the mappings are correctly loaded.

        Todo:
            Test a Codelist that contains a condition.
        """
        mappings = iati.core.codelists.fetch_mappings()

        assert len(mappings) == 92
        # non-embedded Codelist
        assert mappings['//iati-activity/default-finance-type/@code'] == ('FinanceType', None)
        # embedded Codelist
        assert mappings['//iati-activity/planned-disbursement/@type'] == ('BudgetType', None)


class TestCodelists(object):
    """A container for tests relating to Codelists"""

    @pytest.fixture
    def name_to_set(self):
        """A name to give Codelists.

        Returns:
            str: Something that can be provided as a name to Codelists.
        """
        return "test Codelist name"

    def test_codelist_default_attributes(self):
        """Check a Codelist's default attributes are correct"""
        try:
            _ = iati.core.codelists.Codelist()  # pylint: disable=E1120
        except TypeError:
            assert True
        else:
            # a TypeError should have been thrown due to a lack of name
            assert False

    def test_codelist_name_instance(self, name_to_set):
        """Check a Codelist's attributes are correct when defined with only a name"""
        codelist = iati.core.codelists.Codelist(name_to_set)

        assert [] == codelist.codes
        assert codelist.name == name_to_set
        assert codelist.path is None

    def test_codelist_name_and_path_instance(self, name_to_set):
        """Check a Codelist's attributes are correct when defined with a name and path"""
        path_to_set = "test Codelist path"
        codelist = iati.core.codelists.Codelist(name_to_set, path_to_set)

        assert [] == codelist.codes
        assert codelist.name == name_to_set
        assert codelist.path == path_to_set

    def test_codelist_add_code(self, name_to_set):
        """Check a Code can be added to a Codelist"""
        codelist = iati.core.codelists.Codelist(name_to_set)
        code = iati.core.codelists.Code()
        codelist.add_code(code)

        num_codes = len(codelist.codes)

        assert num_codes == 1

    def test_codelist_add_code_decline_non_code(self, name_to_set):
        """Check something that is not a Code cannot be added to a Codelist"""
        codelist = iati.core.codelists.Codelist(name_to_set)
        not_a_code = True
        codelist.add_code(not_a_code)

        num_codes = len(codelist.codes)

        assert num_codes == 0

    def test_codelist_define_from_xml(self, name_to_set):
        """Check that a Codelist can be generated from an XML codelist definition"""
        path = iati.core.resources.path_codelist('FlowType')
        xml_str = iati.core.resources.load_as_string(path)
        codelist = iati.core.codelists.Codelist(name_to_set, xml=xml_str)

        assert codelist.name == 'FlowType'
        assert len(codelist.codes) == 6
        assert codelist.codes[0].value == '10'

    def test_codelist_type_xsd(self, name_to_set):
        """Check that a Codelist can turn itself into a type to use for validation."""
        code_value_to_set = "test Code value"
        codelist = iati.core.codelists.Codelist(name_to_set)
        code = iati.core.codelists.Code(code_value_to_set)
        codelist.add_code(code)

        type_tree = codelist.xsd_tree()

        assert isinstance(type_tree, etree._Element)  # pylint: disable=protected-access
        assert type_tree.tag == iati.core.constants.NAMESPACE + 'simpleType'
        assert type_tree.attrib['name'] == name_to_set + '-type'
        assert type_tree.nsmap == iati.core.constants.NSMAP
        assert len(type_tree) == 1

        assert type_tree[0].tag == iati.core.constants.NAMESPACE + 'restriction'
        assert type_tree[0].nsmap == iati.core.constants.NSMAP
        assert len(type_tree[0]) == 1

        assert type_tree[0][0].tag == iati.core.constants.NAMESPACE + 'enumeration'
        assert type_tree[0][0].attrib['value'] == code_value_to_set
        assert type_tree[0][0].nsmap == iati.core.constants.NSMAP


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

    def test_code_enumeration_element(self):
        """Check that a Code correctly outputs an enumeration element.

        Todo:
            Test enumerating a Code with no value.
        """
        value_to_set = "test Code value"
        code = iati.core.codelists.Code(value_to_set)

        enum_el = code.xsd_tree()

        assert isinstance(enum_el, etree._Element)  # pylint: disable=protected-access
        assert enum_el.tag == iati.core.constants.NAMESPACE + 'enumeration'
        assert enum_el.attrib['value'] == value_to_set
        assert enum_el.nsmap == iati.core.constants.NSMAP
