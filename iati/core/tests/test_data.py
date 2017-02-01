"""A module containing tests for the library representation of IATI data."""
import iati.core.data


class TestDatasets(object):
    """A container for tests relating to Datasets"""

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        pass

    def test_dataset_valid_xml_string(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        pass

    def test_dataset_valid_iati_string(self):
        """Test Dataset creation with a valid IATI XML string."""
        pass

    def test_dataset_invalid_xml_string(self):
        """Test Dataset creation with a string that is not valid XML."""
        pass

    def test_dataset_tree(self):
        """Test Dataset creation with an etree that is not valid IATI data."""
        pass

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
