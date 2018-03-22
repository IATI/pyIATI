"""A module containing tests for the library representation of IATI data.

Todo:
    Implement tests for strict checking once validation work is underway.
"""
import collections
import math
from lxml import etree
import pytest
import iati.data
import iati.default
import iati.tests.utilities


class TestDatasets:
    """A container for tests relating to Datasets."""

    @pytest.fixture
    def dataset_initialised(self):
        """Return an initialised Dataset to work from in other tests."""
        return iati.tests.resources.load_as_dataset('valid_not_iati')

    def test_dataset_no_params(self):
        """Test Dataset creation with no parameters."""
        with pytest.raises(TypeError) as excinfo:
            iati.Dataset()  # pylint: disable=E1120

        assert ('__init__() missing 1 required positional argument' in str(excinfo.value)) or ('__init__() takes exactly 2 arguments' in str(excinfo.value))

    def test_dataset_empty_string(self):
        """Test Dataset creation with an empty string."""
        with pytest.raises(ValueError):
            _ = iati.Dataset('')

    def test_dataset_valid_xml_string(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        xml_str = iati.tests.resources.load_as_string('valid_not_iati')
        data = iati.Dataset(xml_str)

        assert data.xml_str == xml_str.strip()
        assert etree.tostring(data.xml_tree) == etree.tostring(iati.tests.utilities.XML_TREE_VALID)

    def test_dataset_xml_string_leading_whitespace(self):
        """Test Dataset creation with a valid XML string that is not IATI data."""
        xml_str = iati.tests.resources.load_as_string('leading_whitespace_xml')
        data = iati.Dataset(xml_str)
        tree = etree.fromstring(xml_str.strip())

        assert data.xml_str == xml_str.strip()
        assert etree.tostring(data.xml_tree) == etree.tostring(tree)

    def test_dataset_valid_iati_string(self):
        """Test Dataset creation with a valid IATI XML string."""
        pass

    def test_dataset_invalid_xml_string(self):
        """Test Dataset creation with a string that is not valid XML."""
        with pytest.raises(iati.exceptions.ValidationError) as excinfo:
            iati.Dataset(iati.tests.resources.load_as_string('invalid'))

        assert excinfo.value.error_log.contains_error_called('err-not-xml-empty-document')

    @pytest.mark.parametrize("not_xml", iati.tests.utilities.generate_test_types(['bytes', 'str'], True))
    def test_dataset_not_xml(self, not_xml):
        """Test Dataset creation when it's passed a type that is not a string or etree."""
        with pytest.raises(TypeError) as excinfo:
            iati.Dataset(not_xml)

        assert 'Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type:' in str(excinfo.value)

    def test_dataset_tree(self):
        """Test Dataset creation with an etree that is not valid IATI data."""
        tree = iati.tests.utilities.XML_TREE_VALID
        data = iati.Dataset(tree)

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
        xml_str = iati.tests.resources.load_as_string('valid_not_iati')
        data = dataset_initialised
        data.xml_str = xml_str

        assert data.xml_str == xml_str.strip()

    def test_dataset_xml_str_assignment_invalid_str(self, dataset_initialised):
        """Test assignment to the xml_str property with an invalid XML string."""
        xml_str = iati.tests.resources.load_as_string('invalid')
        data = dataset_initialised

        with pytest.raises(iati.exceptions.ValidationError) as excinfo:
            data.xml_str = xml_str

        excinfo.value.error_log.contains_error_called('err-not-xml-empty-document')

    def test_dataset_xml_str_assignment_tree(self, dataset_initialised):
        """Test assignment to the xml_str property with an ElementTree."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = iati.tests.utilities.XML_TREE_VALID

        assert str(excinfo.value) == 'If setting a Dataset with an ElementTree, use the xml_tree property, not the xml_str property.'

    @pytest.mark.parametrize("invalid_value", iati.tests.utilities.generate_test_types(['bytes', 'str']))
    def test_dataset_xml_str_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_str property with a value that is very much not valid."""
        data = dataset_initialised

        with pytest.raises(ValueError):
            data.xml_str = invalid_value

    @pytest.mark.parametrize("invalid_type", iati.tests.utilities.generate_test_types(['bytes', 'str'], True))
    def test_dataset_xml_str_assignment_invalid_type(self, dataset_initialised, invalid_type):
        """Test assignment to the xml_str property with a value that is very much not valid."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_str = invalid_type

        assert 'Datasets can only be ElementTrees or strings containing valid XML, using the xml_tree and xml_str attributes respectively. Actual type:' in str(excinfo.value)

    def test_dataset_xml_tree_assignment_valid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with a valid ElementTree.

        Todo:
            Check that the xml_tree attribute is updated to the new tree.

        """
        data = dataset_initialised
        data.xml_tree = iati.tests.utilities.XML_TREE_VALID

        assert data.xml_str == etree.tostring(iati.tests.utilities.XML_TREE_VALID, pretty_print=True)

    def test_dataset_xml_tree_assignment_invalid_tree(self, dataset_initialised):
        """Test assignment to the xml_tree property with an invalid ElementTree.

        Todo:
            Create an invalid tree and test it.

        """
        pass

    def test_dataset_xml_tree_assignment_str(self, dataset_initialised):
        """Test assignment to the xml_tree property with an XML string."""
        xml_str = iati.tests.resources.load_as_string('valid_not_iati')
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_tree = xml_str

        assert 'If setting a Dataset with the xml_property, an ElementTree should be provided, not a' in str(excinfo.value)

    @pytest.mark.parametrize("invalid_value", iati.tests.utilities.generate_test_types(['str'], True))
    def test_dataset_xml_tree_assignment_invalid_value(self, dataset_initialised, invalid_value):
        """Test assignment to the xml_tree property with a value that is very much not valid."""
        data = dataset_initialised

        with pytest.raises(TypeError) as excinfo:
            data.xml_tree = invalid_value

        assert 'If setting a Dataset with the xml_property, an ElementTree should be provided, not a' in str(excinfo.value)


class TestDatasetWithEncoding:
    """A container for tests relating to creating a Dataset from various types of input.

    This may be files vs strings, or may revolve around character encoding.

    """

    BASE_XML_NEEDING_ENCODING = """<?xml version="1.0" encoding="{}"?>
        <iati-activities version="xx">
          <iati-activity>
             <iati-identifier></iati-identifier>
         </iati-activity>
        </iati-activities>"""

    @pytest.fixture(params=[
        BASE_XML_NEEDING_ENCODING,
        BASE_XML_NEEDING_ENCODING + '\n',  # trailing newline
        BASE_XML_NEEDING_ENCODING + ' '  # trailing space
    ])
    def xml_needing_encoding(self, request):
        """An XML string with a placeholder for an encoding through use of `str.format()`"""
        return request.param

    @pytest.fixture(params=[
        BASE_XML_NEEDING_ENCODING,
        '\n' + BASE_XML_NEEDING_ENCODING,  # leading newline
        ' ' + BASE_XML_NEEDING_ENCODING,  # leading space
        BASE_XML_NEEDING_ENCODING + '\n',  # trailing newline
        BASE_XML_NEEDING_ENCODING + ' '  # trailing space
    ])
    def xml_needing_encoding_use_as_str(self, request):
        """An XML string with a placeholder for an encoding through use of `str.format()`.

        Some values work when used as a `str`, but not as `bytes`.
        """
        return request.param

    def test_instantiation_dataset_from_string(self):
        """Test that a Dataset instantiated directly from a string (rather than a file) correctly creates an iati.data.Dataset and the input data is contained within the object."""
        xml_str = """<?xml version="1.0"?>
        <iati-activities version="xx">
          <iati-activity>
             <iati-identifier></iati-identifier>
         </iati-activity>
        </iati-activities>"""

        dataset = iati.data.Dataset(xml_str)

        assert isinstance(dataset, iati.data.Dataset)
        assert dataset.xml_str == xml_str

    def test_instantiation_dataset_from_string_with_encoding(self, xml_needing_encoding_use_as_str):
        """Test that an encoded Dataset instantiated directly from a string (rather than a file or bytes object) correctly creates an iati.data.Dataset and the input data is contained within the object."""
        xml = xml_needing_encoding_use_as_str.format('UTF-8')

        with pytest.raises(iati.exceptions.ValidationError) as validation_err:
            iati.data.Dataset(xml)

        assert len(validation_err.value.error_log) == 1
        assert validation_err.value.error_log.contains_error_called('err-encoding-in-str')

    @pytest.mark.parametrize("encoding", [
        "UTF-8",
        "utf-8",
        "UTF-16",
        "utf-16",
        "UTF-32",
        "utf-32",
        "ASCII",
        "ISO-8859-1",
        "ISO-8859-2",
        "BIG5",
        "EUC-JP"
    ])
    def test_instantiation_dataset_from_encoded_string_with_encoding(self, xml_needing_encoding, encoding):
        """Test that an encoded Dataset instantiated directly from an encoded string (rather than a file) correctly creates an iati.data.Dataset and the input data is contained within the object.

        Note:
            The use of UTF-8 and UTF-16 is strongly recommended for IATI datasets, however other encodings are specificed here to demonstrate compatibility.

        """
        xml = xml_needing_encoding.format(encoding)
        xml_encoded = xml.encode(encoding)  # Encode the whole string in line with the specified encoding

        dataset = iati.data.Dataset(xml_encoded)

        assert isinstance(dataset, iati.data.Dataset)
        assert dataset.xml_str == xml_encoded.strip()

    @pytest.mark.parametrize("encoding_declared, encoding_used", [
        ("UTF-16", "UTF-8"),
        ("UTF-16", "ISO-8859-1"),
        ("UTF-16", "ASCII"),
        ("UTF-16", "BIG5"),
        ("UTF-16", "EUC-JP")
    ])
    def test_instantiation_dataset_from_encoded_string_with_encoding_mismatch(self, xml_needing_encoding, encoding_declared, encoding_used):
        """Test that an error is raised when attempting to create a Dataset where an encoded string is encoded significantly differently from what is defined within the XML encoding declaration.

        Todo:
            Amend error message, when the todo in iati.data.Dataset.xml_str() has been resolved.

        Note:
            There are a number of other errors that may be raised with alternative encoding mismatches. These are not supported since it does not appear likely enough that they will occur and be a large issue in practice.

            This is due to a pair of issues with libxml2 (the underlying library behind lxml):

            1. It only supports a limited number of encodings out-of-the-box.
            2. Different encoding pairs (whether supported or unsupported by libxml2; byte-equivalent-subsets or distinct encodings; and more), will return different error codes in what one would expect to act as equivalent situations.

        """
        xml = xml_needing_encoding.format(encoding_declared)
        xml_encoded = xml.encode(encoding_used)  # Encode the whole string in line with the specified encoding

        with pytest.raises(iati.exceptions.ValidationError) as excinfo:
            _ = iati.data.Dataset(xml_encoded)

        assert excinfo.value.error_log.contains_error_called('err-encoding-invalid')

    @pytest.mark.parametrize("encoding", ["CP424"])
    def test_instantiation_dataset_from_encoded_string_with_unsupported_encoding(self, xml_needing_encoding, encoding):
        """Test that an error is raised when attempting to create a dataset where an encoded string is encoded significantly differently from what is defined within the XML encoding declaration.

        Todo:
            Amend error message, when the todo in iati.data.Dataset.xml_str() has been resolved.

        """
        xml = xml_needing_encoding.format(encoding)
        xml_encoded = xml.encode(encoding)  # Encode the whole string in line with the specified encoding

        with pytest.raises(iati.exceptions.ValidationError) as excinfo:
            _ = iati.data.Dataset(xml_encoded)

        assert excinfo.value.error_log.contains_error_called('err-encoding-unsupported')


class TestDatasetSourceFinding:
    """A container for tests relating to finding source context within a Dataset."""

    @pytest.fixture(params=[
        iati.tests.resources.load_as_dataset('valid_not_iati'),
        iati.tests.resources.load_as_dataset('valid_iati', '2.02')
    ])
    def data(self, request):
        """A Dataset to test."""
        request.applymarker(pytest.mark.fixed_to_202)

        return request.param

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
        data = iati.tests.resources.load_as_dataset('valid_not_iati')
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

    @pytest.mark.parametrize("invalid_value", iati.tests.utilities.generate_test_types(['int'], True))
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

    @pytest.mark.parametrize("invalid_value", iati.tests.utilities.generate_test_types(['int'], True))
    def test_dataset_xml_str_source_around_line_invalid_context_lines(self, invalid_value, data, num_lines_xml):
        """Test obtaining source of a particular line.

        The specified number of context lines is not an integer.
        """
        for line_num in range(0, num_lines_xml):
            with pytest.raises(TypeError):
                data.source_around_line(line_num, invalid_value)


class TestDatasetVersionDetection:
    """A container for tests relating to detecting the version of a Dataset."""

    @pytest.fixture(params=[
        ('iati-activities', 'iati-activity'),
        ('iati-organisations', 'iati-organisation')
    ])
    def iati_tag_names(self, request):
        """Return the tag names for an activity or organisaion dataset."""
        output = collections.namedtuple('output', 'root_element child_element')
        return output(root_element=request.param[0], child_element=request.param[1])

    def test_detect_version_v1_simple(self, iati_tag_names, std_ver_minor_inst_valid_known_v1):
        """Check that a version 1 Dataset is detected correctly.
        Also checks that version numbers containing whitespace do not affect version detection.
        """
        data = iati.Dataset("""
        <{0} version="{2}">
            <{1} version="{2}"></{1}>
            <{1} version="{2}  "></{1}>
            <{1} version="   {2}"></{1}>
            <{1} version="   {2}   "></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element, std_ver_minor_inst_valid_known_v1))
        result = data.version

        assert result == std_ver_minor_inst_valid_known_v1

    def test_detect_version_explicit_parent_mismatch_explicit_child(self, iati_tag_names):
        """Check that no version is detected for a v1 Dataset where a version within the `iati-activities` element does not match the versions specified within all `iati-activity` child elements."""
        data = iati.Dataset("""
        <{0} version="1.02">
            <{1} version="1.02"></{1}>
            <{1} version="1.03"></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result is None

    def test_detect_version_implicit_parent_matches_implicit_child(self, iati_tag_names):
        """Check that the default version is detected for a Dataset where no versions are declared (i.e. the default version is assumed for all `iati-activities` and `iati-activity` child elements)."""
        data = iati.Dataset("""
        <{0}>
            <{1}></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result == iati.Version('1.01')

    def test_detect_version_explicit_parent_matches_implicit_child(self, iati_tag_names):
        """Check that the default version is detected for a Dataset with the default version explicitly defined at `iati-activities` level, but where all `iati-activity` child elements are not defined (i.e. the default version is assumed)."""
        data = iati.Dataset("""
        <{0} version="1.01">
            <{1}></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result == iati.Version('1.01')

    def test_detect_version_implicit_parent_matches_explicit_and_implicit_child(self, iati_tag_names):
        """Check that the default version is detected for a Dataset with no version not defined at `iati-activities` level (i.e. the default version is assumed), but where at least one `iati-activity` child element has the default version defined."""
        data = iati.Dataset("""
        <{0}>
            <{1} version="1.01"></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result == iati.Version('1.01')

    def test_detect_version_explicit_parent_mismatch_implicit_child(self, iati_tag_names):
        """Check that no version is detected for a Dataset that has a non-default version defined at the `iati-activities` level, but no version is defined in any `iati-activity` child element (i.e. the default version is assumed)."""
        data = iati.Dataset("""
        <{0} version="1.02">
            <{1}></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result is None

    def test_detect_version_imlicit_parent_mismatch_explicit_child(self, iati_tag_names):
        """Check that no version is detected for a Dataset that has no version defined at the `iati-activities` level (i.e. the default version is assumed), but at least one non-default version is defined in any `iati-activity` child element."""
        data = iati.Dataset("""
        <{0}>
            <{1} version="1.02"></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element))
        result = data.version

        assert result is None

    def test_detect_version_v2_simple(self, iati_tag_names, std_ver_minor_inst_valid_known_v2):
        """Check that a version 2 Dataset is detected correctly."""
        data = iati.Dataset("""
        <{0} version="{2}">
            <{1}></{1}>
            <{1}></{1}>
        </{0}>
        """.format(iati_tag_names.root_element, iati_tag_names.child_element, std_ver_minor_inst_valid_known_v2))
        result = data.version

        assert result == std_ver_minor_inst_valid_known_v2

    @pytest.mark.fixed_to_202
    def test_cannot_assign_to_version_property(self):
        """Check that it is not possible to assign to the `version` property."""
        data = iati.tests.resources.load_as_dataset('valid_iati', '2.02')

        with pytest.raises(AttributeError) as excinfo:
            data.version = 'test'

        assert "can't set attribute" in str(excinfo.value)
