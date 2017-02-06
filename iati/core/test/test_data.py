"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.

    Implement tests regarding modification of attributes after the Dataset has initially been created.
"""
from lxml import etree
import iati.core.data
import iati.core.test.utilities


class TestDatasets(object):
    """A container for tests relating to Datasets"""

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        try:
            _ = iati.core.data.Dataset()  # pylint: disable=E1120
        except TypeError:
            assert True
        else:
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
        else:
            # a ValueError should be raised when creating without valid XML
            assert False

    def test_dataset_number_not_xml(self):
        """Test Dataset creation when it's passed a number rather than a string or etree."""
        try:
            _ = iati.core.data.Dataset(17)
        except TypeError:
            assert True
        else:
            # a TypeError should be raised when creating without valid XML
            assert False

    def test_dataset_tree(self):
        """Test Dataset creation with an etree that is not valid IATI data."""
        tree = iati.core.test.utilities.XML_TREE_VALID
        data = iati.core.data.Dataset(tree)

        assert data.xml_tree == tree
        assert data.xml_str == etree.tostring(tree, pretty_print=True)

    def test_dataset_iati_tree(self):
        """Test Dataset creation with a valid IATI etree."""
        pass

    def test_dataset_no_params_strict(self):
        """Test Dataset creation with no parameters.
        Strict IATI checks are enabled.
        """
        pass

    def test_dataset_valid_xml_string_strict(self):
        """Test Dataset creation with a valid XML string that is not IATI data.
        Strict IATI checks are enabled.
        """
        pass

    def test_dataset_valid_iati_string_strict(self):
        """Test Dataset creation with a valid IATI XML string.
        Strict IATI checks are enabled.
        """
        pass

    def test_dataset_invalid_xml_string_strict(self):
        """Test Dataset creation with a string that is not valid XML.
        Strict IATI checks are enabled.
        """
        pass

    def test_dataset_tree_strict(self):
        """Test Dataset creation with an etree that is not valid IATI data.
        Strict IATI checks are enabled.
        """
        pass

    def test_dataset_iati_tree_strict(self):
        """Test Dataset creation with a valid IATI etree.
        Strict IATI checks are enabled.
        """
        pass
