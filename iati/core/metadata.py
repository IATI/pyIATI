"""A module containing metadata classes for IATI SSOT objects."""


class Metadata(object):
    """A base metadata class for all types of IATI SSOT objects."""

    version = None
    orginality = None
    title = None
    description = None


class MetadataCodelist(Metadata):
    """A metadata class for codelist.Codelist objects."""

    category_codelist = None
    codelist_name = None
    complete = None
    ref = None
    revision = None
    source = None
    type = None
    url = None


class MetadataCode(Metadata):
    """A metadata class for codelist.Code objects."""

    activation_date = None
    public_database = None
    status = None
    withdrawl_date = None


class MetadataDataset(Metadata):
    """A metadata class for data.Dataset objects."""

    default_language = None
    languages_contained = set()
    registry_metadata = None  # TODO Add when functionality is added to fetch data directy from the IATI Registry.
    stats = None  # TODO Add when functionality is added to generate statistics from the library
    type = None


class MetadataRuleset(Metadata):
    """A metadata class for rulesets.Rulesets objects."""

    type = None


class MetadataRule(Metadata):
    """A metadata class for rulesets.Rule objects."""

    type = None


class MetadataSchema(Metadata):
    """A metadata class for schemas.Schema objects."""

    default_language = None
    languages_contained = set()
    type = None
