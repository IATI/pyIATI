"""A module containing components that describe the IATI Standard itself (rather than the parts it is made up of)."""
import re
import semantic_version


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

        # a regex for what makes a valid IATIver Version Number format string
        iativer_re = re.compile(r'^((1\.0[1-9])|(((1\d+)|([2-9](\d+)?))\.0[1-9](\d+)?))$')

        # check to see if IATIver
        if iativer_re.match(version_string):
            self.major = int(version_string.split('.')[0])
            self.minor = int(version_string.split('.')[1]) - 1
            self.patch = 0
        else:
            # check to see if SemVer with a positive major version
            if semantic_version.validate(version_string) and semantic_version.Version(version_string).major != 0:
                self.major = int(version_string.split('.')[0])
                self.minor = int(version_string.split('.')[1])
                self.patch = int(version_string.split('.')[2])
            else:
                raise ValueError('A valid version number must be specified.')

    @property
    def integer(self):
        """The IATIver Integer Component of the Version."""
        return self.major

    @property
    def decimal(self):
        """The IATIver Decimal Component of the Version."""
        return self.minor + 1
