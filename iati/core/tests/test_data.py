"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.
"""
import math
from future.standard_library import install_aliases
from lxml import etree
import pytest
import iati.core.data
import iati.core.tests.utilities

install_aliases()


class TestDatasets(object):
    """A container for tests relating to Datasets."""

    @pytest.fixture
    def dataset_initialised(self):
        """Return an initialised dataset to work from in other tests."""
        return iati.core.Dataset(iati.core.tests.utilities.load_as_string('valid_not_iati'))

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        with pytest.raises(TypeError) as excinfo:
            iati.core.Dataset()

        assert ('__init__() missing 1 required positional argument' in str(excinfo.value)) or ('__init__() takes exactly 2 arguments' in str(excinfo.value))

    def test_dataset_valid_xml_string(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        data = iati.core.Dataset(iati.core.tests.utilities.load_as_string('valid_not_iati'))

        assert data.xml_str == iati.core.tests.utilities.load_as_string('valid_not_iati').strip()
        assert etree.tostring(data.xml_tree) == etree.tostring(iati.core.tests.utilities.XML_TREE_VALID)

    def test_dataset_xml_string_leading_whitespace(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        data = iati.core.Dataset(iati.core.tests.utilities.load_as_string('leading_whitespace_xml'))
        tree = etree.fromstring(iati.core.tests.utilities.load_as_string('leading_whitespace_xml').strip())

        assert data.xml_str == iati.core.tests.utilities.load_as_string('leading_whitespace_xml').strip()
        assert etree.tostring(data.xml_tree) == etree.tostring(tree)

    def test_dataset_valid_iati_string(self):
        """Test Dataset creation with a valid IATI XML string."""
        pass

    def test_dataset_invalid_xml_string(self):
        """Test Dataset creation with a string that is not valid XML."""
        with pytest.raises(ValueError) as excinfo:
            iati.core.Dataset(iati.core.tests.utilities.load_as_string('invalid'))

        assert str(excinfo.value) == 'The string provided to create a Dataset from is not valid XML.'

    @pytest.mark.parametrize("not_xml", iati.core.tests.utilities.generate_test_types(['str'], True))
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
        data.xml_str = iati.core.tests.utilities.load_as_string('valid_not_iati')

        assert data.xml_str == iati.core.tests.utilities.load_as_string('valid_not_iati').strip()

    def test_dataset_xml_str_assignment_invalid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with an invalid XML string."""
        data = dataset_initialised

        with pytest.raises(ValueError) as excinfo:
            data.xml_str = iati.core.tests.utilities.load_as_string('invalid')

        assert str(excinfo.value) == 'The string provided to create a Dataset from is not valid XML.'

    def test_dataset_xml_str_assignment_tree(self, dataset_initialised):
        """Test assignment to the xml_str property with an ElementTree."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = iati.core.tests.utilities.XML_TREE_VALID

        assert str(excinfo.value) == 'If setting a dataset with an ElementTree, use the xml_tree property, not the xml_str property.'

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.generate_test_types(['str'], True))
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
            data.xml_tree = iati.core.tests.utilities.load_as_string('valid_not_iati')

        assert 'If setting a dataset with the xml_property, an ElementTree should be provided, not a' in str(excinfo.value)

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.generate_test_types(['str'], True))
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

    @pytest.fixture(params=[
        iati.core.tests.utilities.load_as_string('valid_not_iati'),
        iati.core.tests.utilities.load_as_string('valid_iati')
    ])
    def data(self, request):
        """A Dataset to test."""
        xml_str = request.param.strip()

        return iati.core.Dataset(xml_str)

    @pytest.fixture
    def split_xml_str(self, data):
        """The XML from the provided Dataset, split by line."""
        return [''] + data.xml_str.split('\n')

    @pytest.fixture
    def num_lines_xml(self, split_xml_str):
        """The number of lines in the XML string."""
        return len(split_xml_str)

    def test_dataset_xml_str_source_at_line_valid_line_number(self, data, split_xml_str):
        """Test obtaining source of a particular line. Line numbers are valid."""
        for idx, line in enumerate(split_xml_str):
            assert data.source_at_line(idx) == line.strip()

    @pytest.mark.parametrize("line_el_pair", [
        {'line': 3, 'el': '//parent'},
        {'line': 4, 'el': '//child'},
        {'line': 5, 'el': '//another-child'},
        {'line': 7, 'el': '//sub-child'}
    ])
    def test_dataset_xml_str_source_at_line_matches_tree(self, line_el_pair):
        """Test obtaining source of a particular line. Line numbers are valid.

        Ensure that the line numbers from which source is being returned are the same ones provided by the `sourceline` attribute from tree elements.
        """
        data = iati.core.Dataset(iati.core.tests.utilities.load_as_string('valid_not_iati').strip())
        split_xml_str = [''] + data.xml_str.split('\n')
        line_num = line_el_pair['line']
        el_from_tree = data.xml_tree.xpath(line_el_pair['el'])[0]
        str_from_tree = etree.tostring(el_from_tree, pretty_print=True).strip().decode('utf-8').split('\n')[0]

        assert el_from_tree.sourceline == line_num
        assert data.source_at_line(line_num) == str_from_tree
        assert data.source_at_line(line_num) == split_xml_str[line_num].strip()

    def test_dataset_xml_str_source_at_line_invalid_line_number(self, data, num_lines_xml):
        """Test obtaining source of a particular line. Line numbers are not valid."""
        with pytest.raises(ValueError):
            data.source_at_line(-1)

        with pytest.raises(ValueError):
            data.source_at_line(num_lines_xml)

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.generate_test_types(['int'], True))
    def test_dataset_xml_str_source_at_line_invalid_line_type(self, invalid_value, data):
        """Test obtaining source of a particular line. Line numbers are not valid."""
        with pytest.raises(TypeError):
            data.source_at_line(invalid_value)

    def test_dataset_xml_str_source_around_line_valid_line_number(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The line is in the middle of an XML document so that there will be full context both before and after the specified line number.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        for line_num in range(2, num_lines_xml):
            desired_source = '\n'.join(split_xml_str[line_num - 1:line_num + 2])
            actual_source = data.source_around_line(line_num)

            assert actual_source == desired_source

    def test_dataset_xml_str_source_around_line_valid_line_number_custom_context(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The lines are in the middle of an XML document so that there will be full context both before and after the specified line number.
        Line numbers are valid.
        Uses a custom number of surrounding context lines.
        """
        for context_lines in range(1, math.ceil(num_lines_xml / 2)):
            for line_num in range(context_lines, num_lines_xml - context_lines):
                desired_source = '\n'.join(split_xml_str[max(line_num - context_lines, 1):line_num + context_lines + 1])
                actual_source = data.source_around_line(line_num, context_lines)

                assert actual_source == desired_source

    def test_dataset_xml_str_source_around_line_first_line(self, data, split_xml_str):
        """Test obtaining source around a particular line.

        The line is at the start of an XML document such that there will not be full context before the specified line, but will be afterwards.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        assert data.source_around_line(0) == '\n'.join(split_xml_str[1:2])

    def test_dataset_xml_str_source_around_line_early_line_custom_context(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The lines are around the start of an XML document such that there will not be full context before the specified line, but will be afterwards.
        Line numbers are valid.
        Uses a custom number of surrounding context lines.
        """
        for context_lines in range(1, math.ceil(num_lines_xml / 2)):
            for line_num in range(0, context_lines):
                desired_source = '\n'.join(split_xml_str[1:line_num + context_lines + 1])
                actual_source = data.source_around_line(line_num, context_lines)

                assert actual_source == desired_source

    def test_dataset_xml_str_source_around_line_last_line(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The line is at the end of an XML document such that there will not be full context after the specified line, but will be before.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        assert data.source_around_line(num_lines_xml - 1) == '\n'.join(split_xml_str[-2:])

    def test_dataset_xml_str_source_around_line_late_line_custom_context(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The lines are around the end of an XML document such that there will not be full context after the specified line, but will be before.
        Line numbers are valid.
        Uses the default number of surrounding context lines.
        """
        for context_lines in range(1, math.ceil(num_lines_xml / 2)):
            for line_num in range(0, context_lines):
                desired_source = '\n'.join(split_xml_str[-(line_num + context_lines + 1):])
                actual_source = data.source_around_line(num_lines_xml - line_num - 1, context_lines)

                assert actual_source == desired_source

    def test_dataset_xml_str_source_around_line_single_line(self, data, split_xml_str, num_lines_xml):
        """Test obtaining source around a particular line.

        The context is such that only the specified line will be returned.
        """
        for line_num in range(0, num_lines_xml):
            assert data.source_around_line(line_num, 0) == split_xml_str[line_num]
            assert data.source_around_line(line_num, 0).strip() == data.source_at_line(line_num)

    def test_dataset_xml_str_source_around_line_full_file(self, data, num_lines_xml):
        """Test obtaining source around a particular line.

        The context is such that the full file will be returned.
        """
        line_num = int(num_lines_xml / 2)
        context_lines = num_lines_xml

        assert data.source_around_line(line_num, context_lines) == data.xml_str

    def test_dataset_xml_str_source_around_line_negative_context_lines(self, data, num_lines_xml):
        """Test obtaining source around a particular line.

        The number of context lines is negative.
        """
        for line_num in range(0, num_lines_xml):
            with pytest.raises(ValueError):
                data.source_around_line(line_num, -1)

    @pytest.mark.parametrize("invalid_value", iati.core.tests.utilities.generate_test_types(['int'], True))
    def test_dataset_xml_str_source_around_line_invalid_context_lines(self, invalid_value, data, num_lines_xml):
        """Test obtaining source of a particular line.

        The specified number of context lines is not an integer.
        """
        for line_num in range(0, num_lines_xml):
            with pytest.raises(TypeError):
                data.source_around_line(line_num, invalid_value)
