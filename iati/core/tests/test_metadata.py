"""A module containing tests for Metadata classes."""
import iati.core.metadata


class TestMetadata(object):
    """A container for tests relating to metadata"""

    def test_metadata_instantiation(self):
        """Check that the Metadata class can be created and at least one attribute can be set"""
        metadata = iati.core.metadata.Metadata(version='2.02')

        assert isinstance(metadata, iati.core.metadata.Metadata)
        assert metadata.version == '2.02'

    def test_metadata_codelist_instantiation(self):
        """Check that the MetadataCodelist class can be created and at least one attribute can be set"""
        metadata_codelist = iati.core.metadata.MetadataCodelist(version='2.02', category_codelist='BudgetIdentifierSector')

        assert isinstance(metadata_codelist, iati.core.metadata.MetadataCodelist)
        assert metadata_codelist.version == '2.02'
        assert metadata_codelist.category_codelist == 'BudgetIdentifierSector'

    def test_metadata_code_instantiation(self):
        """Check that the MetadataCode class can be created and at least one attribute can be set"""
        metadata_code = iati.core.metadata.MetadataCode(version='2.02', public_database=True)

        assert isinstance(metadata_code, iati.core.metadata.MetadataCode)
        assert metadata_code.version == '2.02'
        assert metadata_code.public_database is True

    def test_metadata_dataset_instantiation(self):
        """Check that the MetadataDataset class can be created and at least one attribute can be set"""
        metadata_dataset = iati.core.metadata.MetadataDataset(version='2.02', default_language='en')

        assert isinstance(metadata_dataset, iati.core.metadata.MetadataDataset)
        assert metadata_dataset.version == '2.02'
        assert metadata_dataset.default_language == 'en'

    def test_metadata_ruleset_instantiation(self):
        """Check that the MetadataRuleset class can be created and at least one attribute can be set"""
        metadata_ruleset = iati.core.metadata.MetadataRuleset(version='2.02', type='Embedded')

        assert isinstance(metadata_ruleset, iati.core.metadata.MetadataRuleset)
        assert metadata_ruleset.version == '2.02'
        assert metadata_ruleset.type == 'Embedded'

    def test_metadata_rule_instantiation(self):
        """Check that the MetadataRule class can be created and at least one attribute can be set"""
        metadata_rule = iati.core.metadata.MetadataRule(version='2.02')

        assert isinstance(metadata_rule, iati.core.metadata.MetadataRule)
        assert metadata_rule.version == '2.02'

    def test_metadata_schema_instantiation(self):
        """Check that the MetadataSchema class can be created and at least one attribute can be set"""
        metadata_schema = iati.core.metadata.MetadataSchema(version='2.02', default_language='en')

        assert isinstance(metadata_schema, iati.core.metadata.MetadataSchema)
        assert metadata_schema.version == '2.02'
        assert metadata_schema.default_language == 'en'
