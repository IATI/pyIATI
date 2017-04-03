"""A module containing tests for the library representation of validation."""


valid_xml = """
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

invalid_xml = """
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
