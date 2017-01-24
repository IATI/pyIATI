class Codelist(object):
    """Representation of a Codelist as defined within the IATI SSOT"""

    def __init__(self, name=None, path=None):
        self.codes = []
        self.name = name
        self.path = path


class Code(object):
    """Representation of a Code contained within a Codelist"""

    def __init__(self, value=None, name=None):
        self.name = name
        self.value = value
