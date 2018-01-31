"""A module containing components that describe the IATI Standard itself (rather than the parts it is made up of)."""
import re
import semantic_version


class Version(semantic_version.Version):
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

        # check to see if IATIver
        if self._is_iativer(version_string):
            integer = version_string.split('.')[0]
            decimal = str(int(version_string.split('.')[1]) - 1)
            super(Version, self).__init__('.'.join([integer, decimal, '0']), True)
        elif self._is_semver(version_string):
            super(Version, self).__init__(version_string, True)
        else:
            raise ValueError('A valid version number must be specified.')

    @property
    def integer(self):
        """int: The IATIver Integer Component of the Version."""
        return self.major

    @property
    def decimal(self):
        """int: The IATIver Decimal Component of the Version."""
        return self.minor + 1

    @property
    def iativer_str(self):
        """string: An IATIver-format string representation of the Version Number.

        Note:
            The name of this property may change.
        """
        return str(self.integer) + '.0' + str(self.decimal)

    @property
    def semver_str(self):
        """string: A SemVer-format string representation of the Version Number.

        Note:
            The name of this property may change.
        """
        return '.'.join([str(self.major), str(self.minor), str(self.patch)])

    def __repr__(self):
        """str: A representation of the Version Number that will allow a copy of this object to be instantiated."""
        return "iati.Version('" + self.semver_str + "')"

    def __str__(self):
        """str: A representation of the Version Number as would exist on the Version Codelist.

        Warning:
            At present this always results in an IATIver string. This may change should SemVer be adopted.
            The helper methods must be used if a specific format is required.
        """
        return self.iativer_str

    def _is_iativer(self, version_string):
        """Determine whether a version string is in a IATIver format and is a permitted value.

        Args:
            version_string (string): The string to check conformance of.

        Returns:
            bool: True if the provided string is a permitted in IATIver-format version number. False if not.
        """
        # a regex for what makes a valid IATIver Version Number format string
        iativer_re = re.compile(r'^((1\.0[1-9])|(((1\d+)|([2-9](\d+)?))\.0[1-9](\d+)?))$')

        return iativer_re.match(version_string)

    def _is_semver(self, version_string):
        """Determine whether a version string is in a SemVer format and is a permitted value.

        Args:
            version_string (string): The string to check conformance of.

        Returns:
            bool: True if the provided string is a permitted in SemVer-format version number. False if not.
        """
        is_semver_format = semantic_version.validate(version_string)
        try:
            is_permitted_value = semantic_version.Version(version_string).major != 0
        except ValueError:
            return False

        return is_semver_format and is_permitted_value

    def next_major(self):
        """Obtain a Version object that represents the next version after a Major Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Major Upgrade.
        """
        next_major = super(Version, self).next_major()

        return Version(str(next_major))

    def next_minor(self):
        """Obtain a Version object that represents the next version after a Minor Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Minor Upgrade.
        """
        next_minor = super(Version, self).next_minor()

        return Version(str(next_minor))

    def next_integer(self):
        """Obtain a Version object that represents the next version after an Integer Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after an Integer Upgrade.
        """
        return self.next_major()

    def next_decimal(self):
        """Obtain a Version object that represents the next version after a Decimal Upgrade.

        Returns:
            iati.Version: A Version object that represents the next version after a Decimal Upgrade.
        """
        return self.next_minor()

    next_patch = property()
    """Override the parent class's function to provide the next Patch Version.

    Implementation based on https://stackoverflow.com/a/235657

    Note:
        The Error that is raised has a slightly different message than if the attribute had never existed.

    Raises:
        AttributeError: An error that indicates that this attribute does not exist.
    """
