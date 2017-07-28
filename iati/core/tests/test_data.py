"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.
"""
import math
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

        assert data.xml_str == iati.core.tests.utilities.XML_STR_VALID_NOT_IATI.strip()
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

        assert 'The string provided to create a Dataset from is not valid XML.' == str(excinfo.value)

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

        assert data.xml_str == iati.core.tests.utilities.XML_STR_VALID_NOT_IATI.strip()

    def test_dataset_xml_str_assignment_invalid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with an invalid XML string."""
        data = dataset_initialised

        with pytest.raises(ValueError) as excinfo:
            data.xml_str = iati.core.tests.utilities.XML_STR_INVALID

        assert 'The string provided to create a Dataset from is not valid XML.' == str(excinfo.value)

    def test_dataset_xml_str_assignment_tree(self, dataset_initialised):
        """Test assignment to the xml_str property with an ElementTree."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = iati.core.tests.utilities.XML_TREE_VALID

        assert 'If setting a dataset with an ElementTree, use the xml_tree property, not the xml_str property.' == str(excinfo.value)

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

    def test_instantiation_dataset_from_string(self):
        """Test that a dataset instantiated directly from a string (rather than a file) correctly creates an iati.core.data.Dataset and the input data is contained within the object."""
        xml = """<?xml version="1.0"?>
        <iati-activities version="xx">
          <iati-activity>
             <iati-identifier></iati-identifier>
         </iati-activity>
        </iati-activities>"""

        dataset = iati.core.data.Dataset(xml)

        assert isinstance(dataset, iati.core.data.Dataset)
        assert dataset.xml_str == xml

    @pytest.mark.parametrize("encoding", ["UTF-8", "utf-8", "UTF-16", "utf-16",
                                          "ASCII", "ISO-8859-1", "ISO-8859-2",
                                          "BIG5", "EUC-JP"])
    def test_instantiation_dataset_from_string_with_encoding(self, encoding):
        """Test that an encoded dataset instantiated directly from a string (rather than a file) correctly creates an iati.core.data.Dataset and the input data is contained within the object.

        Note:
            The use of UTF-8 and UTF-16 is strongly recommended for IATI datasets, however other encodings are specificed here to demonstrate compatibility.
            UTF-32 is deliberately omitted as this causes an error: lxml.etree.XMLSyntaxError: Document is empty

        """
        xml = """<?xml version="1.0" encoding="{}"?>
        <iati-activities version="xx">
          <iati-activity>
             <iati-identifier></iati-identifier>
         </iati-activity>
        </iati-activities>""".format(encoding)
        xml_encoded = xml.encode(encoding)  # Encode the whole string in line with the specified encoding

        dataset = iati.core.data.Dataset(xml_encoded)

        assert isinstance(dataset, iati.core.data.Dataset)
        assert dataset.xml_str == xml_encoded

    @pytest.mark.parametrize("encoding_declared, encoding_used", [
        ("UTF-16", "UTF-8"),
        ("UTF-16", "ISO-8859-1"),
        ("UTF-16", "BIG5"),
        ("UTF-16", "EUC-JP"),
        ("ASCII", "UTF-16"),
        ("ISO-8859-1", "UTF-16"),
        ("ISO-8859-2", "UTF-16"),
        ("BIG5", "UTF-16"),
        ("EUC-JP", "UTF-16")])
    def test_instantiation_dataset_from_string_with_encoding_mismatch(self, encoding_declared, encoding_used):
        """Test that an error is raised when attempting to create a dataset where a string is encoded significantly differently from what is defined within the XML encoding declaration.

        Todo:
            Amend error message, when the todo in iati.core.data.Dataset.xml_str() has been resolved.

        """
        xml = """<?xml version="1.0" encoding="{}"?>
        <iati-activities version="xx">
          <iati-activity>
             <iati-identifier></iati-identifier>
         </iati-activity>
        </iati-activities>""".format(encoding_declared)
        xml_encoded = xml.encode(encoding_used)  # Encode the whole string in line with the specified encoding

        with pytest.raises(ValueError) as excinfo:
            dataset = iati.core.data.Dataset(xml_encoded)

        assert str(excinfo.value) == 'The string provided to create a Dataset from is not valid XML.'


class TestDatasetSourceFinding(object):
    """A container for tests relating to finding source context within a Dataset."""


    @pytest.fixture
    def data(self):
        """A Dataset to test."""
        xml_str = iati.core.tests.utilities.XML_STR_VALID_NOT_IATI.strip()

        return iati.core.Dataset(xml_str)


    def test_dataset_xml_str_source_at_line_valid_line_number(self, data):
        """Test obtaining source of a particular line. Line numbers are valid."""
        split_xml_str = data.xml_str.split('\n')

        for idx, line in enumerate(split_xml_str):
            assert data.source_at_line(idx) == line.strip()

    def test_dataset_xml_str_source_at_line_invalid_line_number(self, data):
        """Test obtaining source of a particular line. Line numbers are not valid."""
        with pytest.raises(ValueError):
            data.source_at_line(-1)

        with pytest.raises(ValueError):
            data.source_at_line(len(data.xml_str.split('\n')))

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.find_parameter_by_type(['int'], False))
    def test_dataset_xml_str_source_at_line_invalid_line_type(self, invalid_value, data):
        """Test obtaining source of a particular line. Line numbers are not valid."""
        with pytest.raises(TypeError):
            data.source_at_line(invalid_value)

    def test_dataset_xml_str_source_around_line_valid_line_number(self, data):
        """Test obtaining source around a particular line.

        The line is in the middle of an XML document so that there will be full context both before and after the specified line number.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        for line_num in range(1, len(split_xml_str)-1):
            assert data.source_around_line(line_num) == '\n'.join(split_xml_str[line_num-1:line_num+2])

    def test_dataset_xml_str_source_around_line_valid_line_number_custom_context(self, data):
        """Test obtaining source around a particular line.

        The lines are in the middle of an XML document so that there will be full context both before and after the specified line number.
        Line numbers are valid.
        Uses a custom number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        for context_lines in range(1, math.ceil(len(split_xml_str) / 2)):
            for line_num in range(context_lines, len(split_xml_str)-context_lines):
                assert data.source_around_line(line_num, context_lines) == '\n'.join(split_xml_str[line_num-context_lines:line_num+context_lines+1])

    def test_dataset_xml_str_source_around_line_first_line(self, data):
        """Test obtaining source around a particular line.

        The line is at the start of an XML document such that there will not be full context before the specified line, but will be afterwards.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        assert data.source_around_line(0) == '\n'.join(split_xml_str[:2])

    def test_dataset_xml_str_source_around_line_early_line_custom_context(self, data):
        """Test obtaining source around a particular line.

        The lines are around the start of an XML document such that there will not be full context before the specified line, but will be afterwards.
        Line numbers are valid.
        Uses a custom number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        for context_lines in range(1, math.ceil(len(split_xml_str) / 2)):
            for line_num in range(0, context_lines):
                assert data.source_around_line(line_num, context_lines) == '\n'.join(split_xml_str[:line_num + context_lines + 1])

    def test_dataset_xml_str_source_around_line_last_line(self, data):
        """Test obtaining source around a particular line.

        The line is at the end of an XML document such that there will not be full context after the specified line, but will be before.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        assert data.source_around_line(len(split_xml_str) - 1) == '\n'.join(split_xml_str[-2:])

    def test_dataset_xml_str_source_around_line_late_line_custom_context(self, data):
        """Test obtaining source around a particular line.

        The lines are around the end of an XML document such that there will not be full context after the specified line, but will be before.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        split_xml_str = data.xml_str.split('\n')

        for context_lines in range(1, math.ceil(len(split_xml_str) / 2)):
            for line_num in range(0, context_lines):
                assert data.source_around_line(len(split_xml_str) - line_num - 1, context_lines) == '\n'.join(split_xml_str[-(line_num + context_lines + 1):])

    def test_dataset_xml_str_source_around_line_full_file(self, data):
        """Test obtaining source around a particular line.

        The context is such that the full file will be returned.
        """
        split_xml_str = data.xml_str.split('\n')
        line_num = int(len(split_xml_str) / 2)
        context_lines = len(split_xml_str)

        assert data.source_around_line(line_num, context_lines) == data.xml_str
