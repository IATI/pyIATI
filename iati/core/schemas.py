"""
A module containing a core representation of IATI Schemas.
"""


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT"""

    def __init__(self, name=None):
        self.name = name
