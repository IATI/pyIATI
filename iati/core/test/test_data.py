"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.
"""
from lxml import etree
import pytest
import iati.core.data
import iati.core.test.utilities


class TestDatasets(object):
    """A container for tests relating to Datasets"""

    @pytest.fixture
    def dataset_initialised(self):
        """An initialised dataset to work from in other tests."""
        return iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID)

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        try:
            _ = iati.core.data.Dataset()  # pylint: disable=E1120
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without any parameters
            assert False

    def test_dataset_valid_xml_string(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        data = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_VALID)

        assert data.xml_str == iati.core.test.utilities.XML_STR_VALID
        assert etree.tostring(data.xml_tree) == etree.tostring(iati.core.test.utilities.XML_TREE_VALID)

    def test_dataset_valid_iati_string(self):
        """Test Dataset creation with a valid IATI XML string."""
        pass

    def test_dataset_invalid_xml_string(self):
        """Test Dataset creation with a string that is not valid XML."""
        try:
            _ = iati.core.data.Dataset(iati.core.test.utilities.XML_STR_INVALID)
        except ValueError:
            assert True
        else:  # pragma: no cover
            # a ValueError should be raised when creating without valid XML
            assert False

    @pytest.mark.parametrize("not_xml", iati.core.test.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_number_not_xml(self, not_xml):
        """Test Dataset creation when it's passed a number rather than a string or etree."""
        try:
            _ = iati.core.data.Dataset(not_xml)
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without valid XML
            assert False

    def test_dataset_tree(self):
        """Test Dataset creation with an etree that is not valid IATI data."""
        tree = iati.core.test.utilities.XML_TREE_VALID
        data = iati.core.data.Dataset(tree)

        assert data.xml_tree == tree
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
        data.xml_str = iati.core.test.utilities.XML_STR_VALID

        assert data.xml_str == iati.core.test.utilities.XML_STR_VALID

    def test_dataset_xml_str_assignment_invalid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with an invalid XML string."""
        data = dataset_initialised
        try:
            data.xml_str = iati.core.test.utilities.XML_STR_INVALID
        except ValueError:
            assert True
        else:  # pragma: no cover
            # a ValueError should be raised when creating without valid XML
            assert False

    def test_dataset_xml_str_assignment_tree(self, dataset_initialised):
        """Test assignment to the xml_str property with an ElementTree."""
        data = dataset_initialised
        try:
            data.xml_str = iati.core.test.utilities.XML_TREE_VALID
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without valid XML
            assert False

    @pytest.mark.parametrize("invalid_value", iati.core.test.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_xml_str_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_str property with a value that is very much not valid."""
        data = dataset_initialised
        try:
            data.xml_str = invalid_value
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without valid XML
            assert False

    def test_dataset_xml_tree_assignment_valid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with a valid ElementTree.

        Todo:
            Check that the xml_tree attribute is updated to the new tree.
        """
        data = dataset_initialised
        data.xml_tree = iati.core.test.utilities.XML_TREE_VALID

        assert data.xml_str == etree.tostring(iati.core.test.utilities.XML_TREE_VALID, pretty_print=True)

    def test_dataset_xml_tree_assignment_invalid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with an invalid ElementTree.

        Todo:
            Create an invalid tree and test it.
        """
        pass

    def test_dataset_xml_tree_assignment_str(self, dataset_initialised):
        """Test assignment to the xml_tree property with an XML string."""
        data = dataset_initialised
        try:
            data.xml_tree = iati.core.test.utilities.XML_STR_VALID
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without a tree
            assert False

    @pytest.mark.parametrize("invalid_value", iati.core.test.utilities.find_parameter_by_type(['str'], False))
    def test_dataset_xml_tree_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_tree property with a value that is very much not valid."""
        data = dataset_initialised
        try:
            data.xml_tree = invalid_value
        except TypeError:
            assert True
        else:  # pragma: no cover
            # a TypeError should be raised when creating without a tree
            assert False
