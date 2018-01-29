"""A module containing components that describe the IATI Standard itself (rather than the parts it is made up of)."""
import iati.constants


class Version(object):
    """Representation of an IATI Standard Version Number."""

    def __init__(self, version_string):
        """Initialise a Version Number.

        Args:
            version_string (str): A string representation of an IATI version number.

        Raises:
            TypeError: If an attempt to pass something that is not a string is made.
            ValueError: If a provided string is not a version number.

        """
        if not isinstance(version_string, str):
            raise TypeError('A Version object must be created from a string, not a {0}'.format(type(version_string)))

        if version_string not in iati.constants.STANDARD_VERSIONS:
            raise ValueError('A valid version number must be specified.')
