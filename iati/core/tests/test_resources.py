import pytest

import iati.core.resources

class TestResources(object):
    """A container for tests relating to resources"""

    def test_codelist_flow_type(self):
        """Check that the FlowType codelist contains content"""
        path = iati.core.resources.path_codelist('FlowType')

        content = iati.core.resources.load_as_string(path)

        assert 100 < len(content)

    def test_schema_activity(self):
        """Check that the Activity schema contains content"""
        path = iati.core.resources.path_schema('iati-activities-schema')

        content = iati.core.resources.load_as_string(path)

        assert 100 < len(content)
