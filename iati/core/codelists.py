class Codelist(object):
    """Representation of a Codelist as defined within the IATI SSOT"""

    def __init__(self):
        self.codes = []
        self.condition = None
        self.name = None
        self.path = None


class Code(object):
    """Representation of a Code contained within a Codelist"""

    def __init__(self, value=None, name=None):
        self.activation_date = None
        self.name = name
        self.value = value
