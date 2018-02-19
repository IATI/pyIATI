"""Configuration to exist in the global scope for pytest."""
import collections
import pytest
import iati.default
import iati.resources
import iati.tests.utilities
import iati


pytest_plugins = [
    'iati.tests.fixtures.comparison',
    'iati.tests.fixtures.versions'
]


@pytest.fixture(params=[
    ('2.02', 62),  # There are 38 embedded codelists at v2.02, plus 24 non-embedded codelists (which are valid for any version)
    ('2.01', 61),  # There are 37 embedded codelists at v2.01, plus 24 non-embedded codelists (which are valid for any version)
    ('1.05', 59),  # There are 35 embedded codelists at v1.05, plus 24 non-embedded codelists (which are valid for any version)
    ('1.04', 59)  # There are 35 embedded codelists at v1.04, plus 24 non-embedded codelists (which are valid for any version)
])
def codelist_lengths_by_version(request):
    """Return a tuple containing versions of the Standard, and the number of Codelists for that version.

    Format: `(version=[standardVersion], expected_length=[numCodelists])`

    """
    output = collections.namedtuple('output', 'version expected_length')
    return output(version=request.param[0], expected_length=request.param[1])


@pytest.fixture
def schema_ruleset():
    """Return a schema with the Standard Ruleset added.

    Returns:
        A valid Activity Schema with the Standard Ruleset added.

    Todo:
        Stop this being fixed to 2.02.

    """
    schema = iati.default.activity_schema('2.02', False)
    ruleset = iati.default.ruleset('2.02')

    schema.rulesets.add(ruleset)

    return schema
