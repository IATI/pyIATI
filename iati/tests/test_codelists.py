"""A module containing tests for the library representation of Codelists."""
import copy
import pytest
from lxml import etree
import iati.codelists


class TestCodelistsNonClass(object):
    """Test codelists functionality that is not contained within a class.

    Note:
        There was once functionality regarding mapping files here. That was removed.
    """

    pass


class TestCodelists(object):
    """A container for tests relating to Codelists."""

    @pytest.fixture
    def name_to_set(self):
        """Set a name to give Codelists.

        Returns:
            str: Something that can be provided as a name to Codelists.

        """
        return "test Codelist name"

    def test_codelist_default_attributes(self):
        """Check a Codelist's default attributes are correct."""
        with pytest.raises(TypeError) as excinfo:
            iati.Codelist()  # pylint: disable=E1120

        assert ('__init__() missing 1 required positional argument' in str(excinfo.value)) or ('__init__() takes at least 2 arguments' in str(excinfo.value))

    def test_codelist_name_instance(self, name_to_set):
        """Check a Codelist's attributes are correct when defined with only a name."""
        codelist = iati.Codelist(name_to_set)

        assert set() == codelist.codes
        assert codelist.name == name_to_set

    def test_codelist_add_code(self, name_to_set):
        """Check a Code can be added to a Codelist."""
        codelist = iati.Codelist(name_to_set)
        code = iati.Code()
        codelist.codes.add(code)

        num_codes = len(codelist.codes)

        assert num_codes == 1

    @pytest.mark.xfail
    def test_codelist_add_code_decline_non_code(self, name_to_set):
        """Check something that is not a Code cannot be added to a Codelist."""
        codelist = iati.Codelist(name_to_set)
        not_a_code = True
        codelist.codes.add(not_a_code)

        num_codes = len(codelist.codes)

        assert num_codes == 0

    def test_codelist_define_from_xml(self, name_to_set):
        """Check that a Codelist can be generated from an XML codelist definition."""
        path = iati.resources.get_codelist_path('FlowType')
        xml_str = iati.utilities.load_as_string(path)
        codelist = iati.Codelist(name_to_set, xml=xml_str)

        code_names = ['ODA', 'OOF', 'Private grants', 'Private Market', 'Non flow', 'Other flows']
        code_values = ['10', '20', '30', '35', '40', '50']

        assert codelist.name == 'FlowType'
        assert len(codelist.codes) == 6
        for code in codelist.codes:
            assert code.name in code_names
            assert code.value in code_values

    def test_codelist_complete(self):
        """Check that a Codelist can be generated from an XML codelist definition."""
        codelist_name = 'BudgetType'
        path = iati.resources.get_codelist_path(codelist_name)
        xml_str = iati.utilities.load_as_string(path)
        codelist = iati.Codelist(codelist_name, xml=xml_str)

        assert codelist.complete is True

    def test_codelist_incomplete(self):
        """Check that a Codelist can be generated from an XML codelist definition."""
        codelist_name = 'Country'
        path = iati.resources.get_codelist_path(codelist_name)
        xml_str = iati.utilities.load_as_string(path)
        codelist = iati.Codelist(codelist_name, xml=xml_str)

        assert codelist.complete is False

    def test_codelist_type_xsd(self, name_to_set):
        """Check that a Codelist can turn itself into a type to use for validation."""
        code_value_to_set = "test Code value"
        codelist = iati.Codelist(name_to_set)
        code = iati.Code(code_value_to_set)
        codelist.codes.add(code)

        type_tree = codelist.xsd_restriction

        assert isinstance(type_tree, etree._Element)  # pylint: disable=protected-access
        assert type_tree.tag == iati.constants.NAMESPACE + 'simpleType'
        assert type_tree.attrib['name'] == name_to_set + '-type'
        assert type_tree.nsmap == iati.constants.NSMAP
        assert len(type_tree) == 1

        assert type_tree[0].tag == iati.constants.NAMESPACE + 'restriction'
        assert type_tree[0].nsmap == iati.constants.NSMAP
        assert len(type_tree[0]) == 1

        assert type_tree[0][0].tag == iati.constants.NAMESPACE + 'enumeration'
        assert type_tree[0][0].attrib['value'] == code_value_to_set
        assert type_tree[0][0].nsmap == iati.constants.NSMAP


class TestCodes(object):
    """A container for tests relating to Codes."""

    def test_code_default_attributes(self):
        """Check a Code's default attributes are correct."""
        code = iati.Code()

        assert code.name == ''
        assert code.value is None

    def test_code_value_instance(self):
        """Check a Code's attributes are correct when being defined with only a value."""
        value_to_set = "test Code value"
        code = iati.Code(value_to_set)

        assert code.name == ''
        assert code.value == value_to_set

    def test_code_value_and_name_instance(self):
        """Check a Code's attributes are correct when being defined with a value and name."""
        value_to_set = "test Code value"
        name_to_set = "test Code name"
        code = iati.Code(value_to_set, name_to_set)

        assert code.name == name_to_set
        assert code.value == value_to_set

    def test_code_enumeration_element(self):
        """Check that a Code correctly outputs an enumeration element.

        Todo:
            Test enumerating a Code with no value.

        """
        value_to_set = "test Code value"
        code = iati.Code(value_to_set)

        enum_el = code.xsd_enumeration

        assert isinstance(enum_el, etree._Element)  # pylint: disable=protected-access
        assert enum_el.tag == iati.constants.NAMESPACE + 'enumeration'
        assert enum_el.attrib['value'] == value_to_set
        assert enum_el.nsmap == iati.constants.NSMAP


class TestCodelistEquality(object):
    """A container for tests relating to Codelist equality - both direct and via hashing."""

    @pytest.fixture(params=[
        lambda x, y: x == y,
        lambda x, y: hash(x) == hash(y)
    ])
    def cmp_func_equal(self, request):
        """Return a comparison function that checks whether things are equal."""
        return request.param

    @pytest.fixture(params=[
        lambda x, y: x != y,
        lambda x, y: hash(x) != hash(y)
    ])
    def cmp_func_different(self, request):
        """Return a comparison function that checks whether things are different."""
        return request.param

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_same_object_equal(self, codelist, cmp_func_equal):
        """Check that a Codelist is deemed to be equal with itself."""
        assert cmp_func_equal(codelist, codelist)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_same_diff_object_equal(self, codelist, cmp_func_equal):
        """Check that two instances of the same Codelist are deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)

        assert cmp_func_equal(codelist, codelist_copy)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_name_not_equal(self, codelist, cmp_func_different):
        """Check that two Codelist with the same codes but different names are not deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)
        codelist_copy.name = codelist.name + 'with a difference'

        assert cmp_func_different(codelist, codelist_copy)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_completeness_not_equal(self, codelist, cmp_func_different):
        """Check that two Codelist with the same codes but different completeness are not deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)
        codelist_copy.complete = not codelist.complete

        assert cmp_func_different(codelist, codelist_copy)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_num_codes_not_equal(self, codelist, cmp_func_different):
        """Check that two Codelist with the same name but different codes are not deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)
        codelist_copy.codes.add(iati.Code())

        assert cmp_func_different(codelist, codelist_copy)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_code_name_not_equal(self, codelist):
        """Check that two Codelist with the same name but a Code with a different name are not deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)
        code = codelist_copy.codes.pop()
        code.name = code.name + 'with a difference'
        codelist_copy.codes.add(code)

        assert codelist != codelist_copy

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_code_name_same_hash(self, codelist):
        """Check that two Codelist with the same name but a Code with a different name have the same hash."""
        codelist_copy = copy.deepcopy(codelist)
        code = codelist_copy.codes.pop()
        code.name = code.name + 'with a difference'
        codelist_copy.codes.add(code)

        assert hash(codelist) == hash(codelist_copy)

    @pytest.mark.parametrize('codelist', iati.default.codelists('2.02').values())
    def test_codelist_diff_code_value_not_equal(self, codelist, cmp_func_different):
        """Check that two Codelist with the same name but a Code with a different value are not deemed to be equal."""
        codelist_copy = copy.deepcopy(codelist)
        code = codelist_copy.codes.pop()
        code.value = code.value + 'with a difference'
        codelist_copy.codes.add(code)

        assert cmp_func_different(codelist, codelist_copy)
