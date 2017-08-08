"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.
"""
from lxml import etree
import pytest
import iati.core.data
import iati.core.tests.utilities


class TestDatasets(object):
    """A container for tests relating to Datasets."""

    @pytest.fixture
    def dataset_initialised(self):
        """Return an initialised dataset to work from in other tests."""
        return iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        with pytest.raises(TypeError) as excinfo:
            iati.core.Dataset()

        assert ('__init__() missing 1 required positional argument' in str(excinfo.value)) or ('__init__() takes exactly 2 arguments' in str(excinfo.value))

    def test_dataset_valid_xml_string(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_VALID_NOT_IATI)

        assert data.xml_str == iati.core.tests.utilities.XML_STR_VALID_NOT_IATI
        assert etree.tostring(data.xml_tree) == etree.tostring(iati.core.tests.utilities.XML_TREE_VALID)

    def test_dataset_xml_string_leading_whitespace(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        data = iati.core.Dataset(iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE)
        tree = etree.fromstring(iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE.strip())

        assert data.xml_str == iati.core.tests.utilities.XML_STR_LEADING_WHITESPACE.strip()
        assert etree.tostring(data.xml_tree) == etree.tostring(tree)

    def test_dataset_valid_iati_string(self):
        """Test Dataset creation with a valid IATI XML string."""
        pass

    def test_dataset_invalid_xml_string(self):
        """Test Dataset creation with a string that is not valid XML."""
        with pytest.raises(ValueError) as excinfo:
            iati.core.Dataset(iati.core.tests.utilities.XML_STR_INVALID)

        assert str(excinfo.value) == 'The string provided to create a Dataset from is not valid XML.'

    @pytest.mark.parametrize("not_xml", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_number_not_xml(self, not_xml):
        """Test Dataset creation when it's passed a number rather than a string or etree."""
        with pytest.raises(TypeError) as excinfo:
            iati.core.Dataset(not_xml)

        assert 'Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type:' in str(excinfo.value)

    def test_dataset_tree(self):
        """Test Dataset creation with an etree that is not valid IATI data."""
        tree = iati.core.tests.utilities.XML_TREE_VALID
        data = iati.core.Dataset(tree)

        assert etree.tostring(data.xml_tree, pretty_print=True) == etree.tostring(tree, pretty_print=True)
        assert data.xml_str == etree.tostring(tree, pretty_print=True)

    def test_dataset_iati_tree(self):
        """Test Dataset creation with a valid IATI etree.

        Todo:
            Implement this function.

        """
        pass

    def test_dataset_xml_str_assignment_valid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with a valid XML string.

        Todo:
            Check that the tree is updated correctly.

        """
        data = dataset_initialised
        data.xml_str = iati.core.tests.utilities.XML_STR_VALID_NOT_IATI

        assert data.xml_str == iati.core.tests.utilities.XML_STR_VALID_NOT_IATI

    def test_dataset_xml_str_assignment_invalid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with an invalid XML string."""
        data = dataset_initialised

        with pytest.raises(ValueError) as excinfo:
            data.xml_str = iati.core.tests.utilities.XML_STR_INVALID

        assert str(excinfo.value) == 'The string provided to create a Dataset from is not valid XML.'

    def test_dataset_xml_str_assignment_tree(self, dataset_initialised):
        """Test assignment to the xml_str property with an ElementTree."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = iati.core.tests.utilities.XML_TREE_VALID

        assert str(excinfo.value) == 'If setting a dataset with an ElementTree, use the xml_tree property, not the xml_str property.'

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_xml_str_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_str property with a value that is very much not valid."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = invalid_value

        assert 'Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type:' in str(excinfo.value)

    def test_dataset_xml_tree_assignment_valid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with a valid ElementTree.

        Todo:
            Check that the xml_tree attribute is updated to the new tree.

        """
        data = dataset_initialised
        data.xml_tree = iati.core.tests.utilities.XML_TREE_VALID

        assert data.xml_str == etree.tostring(iati.core.tests.utilities.XML_TREE_VALID, pretty_print=True)

    def test_dataset_xml_tree_assignment_invalid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with an invalid ElementTree.

        Todo:
            Create an invalid tree and test it.

        """
        pass

    def test_dataset_xml_tree_assignment_str(self, dataset_initialised):
        """Test assignment to the xml_tree property with an XML string."""
        data = dataset_initialised
        with pytest.raises(TypeError) as excinfo:
            data.xml_tree = iati.core.tests.utilities.XML_STR_VALID_NOT_IATI

        assert 'If setting a dataset with the xml_property, an ElementTree should be provided, not a' in str(excinfo.value)

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_xml_tree_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_tree property with a value that is very much not valid."""
        data = dataset_initialised
        with pytest.raises(TypeError) as excinfo:
            data.xml_tree = invalid_value

        assert 'If setting a dataset with the xml_property, an ElementTree should be provided, not a' in str(excinfo.value)
