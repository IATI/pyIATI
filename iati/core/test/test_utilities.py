"""A module containing tests for the library implementation of accessing utilities."""
from lxml import etree
import iati.core.resources
import iati.core.utilities


class TestUtilities(object):
    """A container for tests relating to utilities"""

    def test_convert_tree_to_schema(self):
        """Check that an etree can be converted to a schema."""
        path = iati.core.resources.path_schema('iati-activities-schema')

        tree = iati.core.resources.load_as_tree(path)
        if not tree:  # pragma: no cover
            assert False
        schema = iati.core.utilities.convert_tree_to_schema(tree)

        assert isinstance(schema, etree.XMLSchema)

    def test_convert_xml_to_tree(self):
        """Check that a valid XML string can be converted to an etree."""
        xml = '<parent><child /></parent>'

        tree = iati.core.utilities.convert_xml_to_tree(xml)

        assert isinstance(tree, etree._Element)  # pylint: disable=protected-access
        assert tree.tag == 'parent'
        assert len(tree.getchildren()) == 1
        assert tree.getchildren()[0].tag == 'child'
        assert len(tree.getchildren()[0].getchildren()) == 0

    def test_log(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_error(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_exception(self):
        """TODO: Implement testing for logging."""
        pass

    def test_log_warning(self):
        """TODO: Implement testing for logging."""
        pass
