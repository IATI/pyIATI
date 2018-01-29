"""A module containing components that describe the IATI Standard itself (rather than the parts it is made up of)."""
import iati.constants


class Version(object):
    """Representation of an IATI Standard Version Number."""

    def __init__(self, version_string):
        """Initialise a Version Number."""
        if not isinstance(version_string, str):
            raise TypeError('A Version object must be created from a string, not a {0}'.format(type(version_string)))

        if not version_string in iati.constants.STANDARD_VERSIONS:
            raise ValueError('A valid version number must be specified.')

