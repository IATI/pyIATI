"""Configuration to exist in the global scope for pytest."""
import collections
import pytest
import iati.default
import iati.resources
import iati.tests.utilities
import iati


pytest_plugins = [  # name required by pytest  # pylint: disable=invalid-name
    'iati.tests.fixtures.comparison',
    'iati.tests.fixtures.filepaths',
    'iati.tests.fixtures.versions'
]


def _check_latest_version_mark(item):
    """Check that functions marked as supporting the latest version of the IATI Standard have been updated."""
    latest_version_marker = item.get_marker('latest_version')
    if latest_version_marker is not None:
        latest_version = iati.Version(latest_version_marker.args[0])
        assert latest_version == iati.version.STANDARD_VERSION_LATEST


def pytest_runtest_call(item):
    """Run operations that are called when tests are run."""
    _check_latest_version_mark(item)


@pytest.fixture(params=[
    ('2.03', 66),  # There are 9 embedded codelists at v2.03, plus 57 non-embedded codelists (which are valid for any version)
    ('2.02', 66),  # There are 9 embedded codelists at v2.02, plus 57 non-embedded codelists (which are valid for any version)
    ('2.01', 65),  # There are 8 embedded codelists at v2.01, plus 57 non-embedded codelists (which are valid for any version)
    ('1.05', 67),  # There are 10 embedded codelists at v1.05, plus 57 non-embedded codelists (which are valid for any version)
    ('1.04', 67),  # There are 10 embedded codelists at v1.04, plus 57 non-embedded codelists (which are valid for any version)
    ('2', 66),  # the same as the latest minor within the major
    ('1', 67)  # the same as the latest minor within the major
])
def codelist_lengths_by_version(request):  # latest_version fixture used to perform checks when adding new versions  # pylint: disable=unused-argument
    """Return a tuple containing versions of the Standard, and the number of Codelists for that version.

    Format: `(version=[standardVersion], expected_length=[numCodelists])`

    """
    request.applymarker(pytest.mark.latest_version('2.03'))

    output = collections.namedtuple('output', 'version expected_length')
    return output(version=request.param[0], expected_length=request.param[1])


@pytest.fixture
def schema_ruleset(request):
    """Return a schema with the Standard Ruleset added.

    Returns:
        A valid Activity Schema with the Standard Ruleset added.

    """
    request.applymarker(pytest.mark.fixed_to_202)

    schema = iati.default.activity_schema('2.02', False)
    ruleset = iati.default.ruleset('2.02')

    schema.rulesets.add(ruleset)

    return schema
