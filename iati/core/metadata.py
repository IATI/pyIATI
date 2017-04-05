"""A module containing metadata classes for IATI SSOT objects."""


class Metadata(object):
    """A base metadata class for all types of IATI SSOT objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.version = kwargs.pop('version', None)
        self.orginality = kwargs.pop('orginality', None)
        self.title = kwargs.pop('title', None)
        self.description = kwargs.pop('description', None)


class MetadataCodelist(Metadata):
    """A metadata class for codelist.Codelist objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.category_codelist = kwargs.pop('category_codelist', None)
        self.codelist_name = kwargs.pop('codelist_name', None)
        self.complete = kwargs.pop('complete', None)
        self.ref = kwargs.pop('ref', None)
        self.revision = kwargs.pop('revision', None)
        self.source = kwargs.pop('source', None)
        self.type = kwargs.pop('type', None)
        self.url = kwargs.pop('url', None)
        Metadata.__init__(self, **kwargs)


class MetadataCode(Metadata):
    """A metadata class for codelist.Code objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.activation_date = kwargs.pop('activation_date', None)
        self.public_database = kwargs.pop('public_database', None)
        self.status = kwargs.pop('status', None)
        self.withdrawl_date = kwargs.pop('withdrawl_date', None)
        Metadata.__init__(self, **kwargs)


class MetadataDataset(Metadata):
    """A metadata class for data.Dataset objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.default_language = kwargs.pop('default_language', None)
        self.languages_contained = set()
        self.registry_metadata = dict()  # TODO Add when functionality is added to fetch data directy from the IATI Registry.
        self.stats = None  # TODO Add when functionality is added to generate statistics from the library
        self.type = kwargs.pop('type', None)
        Metadata.__init__(self, **kwargs)


class MetadataRuleset(Metadata):
    """A metadata class for rulesets.Rulesets objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.type = kwargs.pop('type', None)
        Metadata.__init__(self, **kwargs)


class MetadataRule(Metadata):
    """A metadata class for rulesets.Rule objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.type = kwargs.pop('type', None)
        Metadata.__init__(self, **kwargs)


class MetadataSchema(Metadata):
    """A metadata class for schemas.Schema objects."""

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.default_language = kwargs.pop('default_language', None)
        self.languages_contained = set()
        self.type = kwargs.pop('type', None)
        Metadata.__init__(self, **kwargs)
