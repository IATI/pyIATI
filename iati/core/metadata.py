"""A module containing metadata classes for IATI SSOT objects."""

from enum import Enum


class Metadata(object):
    """A base metadata class for all forms of IATI SSOT objects.

    Todo:
        Incorportate advice on Enum usage from stackexchange post: https://codereview.stackexchange.com/questions/162513/enum-usage-to-restrict-class-attribute-values/
        Add documentation for class attributes.
    """

    OrginalityTypes = Enum('OrginalityTypes', 'original modified', module=__name__)

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.description = kwargs.pop('description', None)
        self.orginality = kwargs.pop('orginality', None)
        self.title = kwargs.pop('title', None)
        self.version = kwargs.pop('version', None)

    def is_in_enum(self, value, Enum):
        """Verify that a value is contained within a defined Enum object.

        Params:
            value (str): Value to be checked.
            Enum (Enum): Enum object containing allowed values.

        Returns:
            True: If the Enum is contained within the defined Enum.

        Raises:
            ValueError: If the value is not contained within the defined Enum.
        """
        if value in Enum.__members__:
            return True
        else:
            raise ValueError("Value {0} not in Enum list.".format(value))

    def set_attr_by_enum(self, value, Enum):
        """Helper function to set a class attribute to None (if the input value is None), or to a value (if it is contained within an input Enum).

        Params:
            value (str): Value to be checked.
            Enum (Enum): Enum object containing allowed values.

        Returns:
            None: If the input value is None
            Value: If the input value is contained within the Enum
        """
        if value is None:
            return None
        elif self.is_in_enum(value, Enum):
            return value  # is_in_enum() raises a ValueError exception if not True

class MetadataCodelist(Metadata):
    """A metadata class for codelist.Codelist objects.

    Todo:
        Add documentation for class attributes.
    """

    CodelistTypes = Enum('CodelistTypes', 'embedded non-embedded user-defined', module=__name__)
    SourceTypes = Enum('SourceTypes', 'iati replicated user-defined', module=__name__)

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.category_codelist = kwargs.pop('category_codelist', None)
        self.codelist_name = kwargs.pop('codelist_name', None)
        self.codelist_type = self.set_attr_by_enum(kwargs.pop('codelist_type', None), self.CodelistTypes)
        self.complete = kwargs.pop('complete', None)
        self.ref = kwargs.pop('ref', None)
        self.revision = kwargs.pop('revision', None)
        self.source = kwargs.pop('source', None)
        self.url = kwargs.pop('url', None)
        Metadata.__init__(self, **kwargs)


class MetadataCode(Metadata):
    """A metadata class for codelist.Code objects.

    Todo:
        Add documentation for class attributes.
    """

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.activation_date = kwargs.pop('activation_date', None)
        self.public_database = kwargs.pop('public_database', None)
        self.status = kwargs.pop('status', None)
        self.withdrawl_date = kwargs.pop('withdrawl_date', None)
        Metadata.__init__(self, **kwargs)


class MetadataDataset(Metadata):
    """A metadata class for data.Dataset objects.

    Todo:
        Add documentation for class attributes.
    """

    DatasetTypes = Enum('DatasetTypes', 'activity activity-partial organisation organisation-partial', module=__name__)

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.dataset_type = kwargs.pop('dataset_type', None)
        self.default_language = kwargs.pop('default_language', None)
        self.languages_contained = set()
        self.registry_metadata = dict()  # TODO Add when functionality is added to fetch data directy from the IATI Registry.
        self.stats = None  # TODO Add when functionality is added to generate statistics from the library
        Metadata.__init__(self, **kwargs)


class MetadataRuleset(Metadata):
    """A metadata class for rulesets.Rulesets objects.

    Todo:
        Add documentation for class attributes.
    """

    RulesetTypes = Enum('RulesetTypes', 'embedded user-defined', module=__name__)

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.ruleset_type = kwargs.pop('ruleset_type', None)
        Metadata.__init__(self, **kwargs)


class MetadataRule(Metadata):
    """A metadata class for rulesets.Rule objects.

    No further metadata is required for rulesets.Rule objects, but this is added for completeness.
    """

    pass


class MetadataSchema(Metadata):
    """A metadata class for schemas.Schema objects.

    Todo:
        Add documentation for class attributes.
    """

    SchemaTypes = Enum('SchemaTypes', 'activity codelist common organisation', module=__name__)

    def __init__(self, **kwargs):
        """Set class attributes."""
        self.default_language = kwargs.pop('default_language', None)
        self.languages_contained = set()
        self.schema_type = kwargs.pop('schema_type', None)
        Metadata.__init__(self, **kwargs)
