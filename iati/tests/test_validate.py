"""A module containing tests for data validation."""
import iati.core.data
import iati.core.default
import iati.core.schemas
import iati.core.tests.utilities
import iati.validate


VALID_XML = """
<?xml version="1.0"?>

<iati-activities version="2.02">
  <iati-activity>
    <iati-identifier></iati-identifier>
    <reporting-org type="40" ref="AA-AAA-123456789">
      <narrative>Organisation name</narrative>
    </reporting-org>
    <title>
      <narrative>Xxxxxxx</narrative>
    </title>
    <description>
      <narrative>Xxxxxxx</narrative>
    </description>
    <participating-org role="2"></participating-org>
    <activity-status code="2"/>
    <activity-date type="1" iso-date="2023-11-27"/>
  </iati-activity>
</iati-activities>
"""

INVALID_XML = """
<?xml version="1.0"?>

<iati-activities version="200.02"><!-- Invalid Version -->
  <iati-activity>
    <iati-identifier></iati-identifier>
    <reporting-org type="40" ref="AA-AAA-123456789">
      <narrative>Organisation name</narrative>
    </reporting-org>
    <title>
      <narrative>Xxxxxxx</narrative>
    </title>
    <description>
      <narrative>Xxxxxxx</narrative>
    </description>
    <participating-org role="2"></participating-org>
    <activity-status code="2"/>
    <activity-date type="1" iso-date="2023-11-27"/>
  </iati-activity>
</iati-activities>
"""


class TestValidate(object):
    """A container for tests relating to validation."""

    def test_basic_validation_valid(self):
        """Perform a super simple data validation against a valid Dataset."""
        data = iati.core.data.Dataset(VALID_XML)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

        assert iati.validate.is_valid(data, schema)

    # @pytest.mark.xfail
    # def test_basic_validation_invalid(self):
    #     """Perform super simple data validation against a valid dataset"""
    #     data = iati.core.data.Dataset(iati.core.tests.utilities.XML_STR_VALID)
    #     schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)

    #     assert not iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_valid(self):
        """Perform data validation against valid IATI XML that has valid Codelist values."""
        data = iati.core.data.Dataset(VALID_XML)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert iati.validate.is_valid(data, schema)

    def test_basic_validation_codelist_invalid(self):
        """Perform data validation against valid IATI XML that has invalid Codelist values."""
        data = iati.core.data.Dataset(INVALID_XML)
        schema = iati.core.schemas.Schema(name=iati.core.tests.utilities.SCHEMA_NAME_VALID)
        codelist = iati.core.default.codelists()['Version']

        schema.codelists.add(codelist)

        assert not iati.validate.is_valid(data, schema)
