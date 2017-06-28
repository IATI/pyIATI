"""A module containing a core representation of IATI Schemas."""
import copy
import uuid
from lxml import etree
import iati.core.codelists
import iati.core.constants
import iati.core.exceptions
import iati.core.resources
import iati.core.utilities


class Schema(object):
    """Represenation of a Schema as defined within the IATI SSOT.

    Attributes:
        name (str): The name of the Schema.
        codelists (set): The Codelists asspciated with this Schema. This is a read-only attribute.

    Warning:
        The private attribute allowing access to the base Schema Tree is likely to change in determining a good way of accessing the contained schema content.

    Todo:
        Determine a good API for accessing the XMLSchema that the iati.core.schemas.Schema represents.

        Determine how to distinguish and handle the different types of Schema - activity, organisation, codelist, other.
    """

    def __init__(self, name=None):
        """Initialise a Schema.

        Args:
            name (str): The name of the schema being initialised.
                This name refers to a file contained within the core IATI resources folder.

        Raises:
            TypeError: The type of the provided name is incorrect.
            iati.core.exceptions.SchemaError: An error occurred during the creation of the Schema.

        Warning:
            The format of the constructor is likely to change. It needs to be less reliant on the name acting as a UID, and allow for other attributes to be provided at this point.

            The raised exceptions are likely to change upon review of IATI-specific exceptions.

            Need to define a good API for accessing public and private attributes. Requiring something along the lines of `schema.schema` is likely not ideal. An improved understanding of use cases will be required for this.

        Todo:
            Allow for generation of schemas outside the IATI SSOT.

            Better use the try-except pattern.

            Allow the base schema to be modified after initialisation.

            Create test instance where the SchemaError is raised.
        """
        self.name = name
        self._schema_base_tree = None
        self.codelists = set()

        if isinstance(name, str):
            path = iati.core.resources.path_schema(self.name)
            try:
                loaded_tree = iati.core.resources.load_as_tree(path)
            except (IOError, OSError):
                msg = "Failed to load tree at '{0}' when creating Schema.".format(path)
                iati.core.utilities.log_error(msg)
                raise iati.core.exceptions.SchemaError
            else:
                self._schema_base_tree = loaded_tree
        elif name is not None:
            msg = "The name of the Schema is an invalid type. Must be a string, though was a {0}.".format(type(name))
            iati.core.utilities.log_error(msg)
            raise TypeError(msg)

    def validator(self, dataset):
        """A schema that can be used for validation.

        Takes the base schema and dynamically injects elements for content checking.

        Params:
            dataset (iati.core.data.Dataset): A Dataset to create a validator for. This makes it possible to deal with vocabularies.

        Returns:
            etree.XMLSchema: A schema that can be used for validation.
        Todo:
            Implement Codelist content checking.
            Implement Ruleset content checking.
            Add configuration parameters.
            Add tests when dataset is not provided.
        """
        def get_sector_vocab(dataset):
            """Find the sector vocabulary within a Dataset.

            Params:
                dataset (iati.core.data.Dataset): A Dataset to find a sector vocabulary within.

            Returns:
                str: The vocabulary to be used.

            Todo:
                Add exception documentation.
            """
            if dataset is None:
                vocab = '1'  # TODO: Lose the magic number for default
            elif isinstance(dataset, iati.core.data.Dataset):
                try:
                    vocab = dataset.xml_tree.find('//iati-activity/sector').get('vocabulary')
                    if vocab is None:
                        vocab = '1'
                except Exception as e:  # TODO: Use a less general exception
                    # cannot find @vocabulary, so use default vocab
                    vocab = '1'
            else:
                # TODO: Raise TypeError
                pass

            return vocab

        # tree = copy.deepcopy(self._schema_base_tree)
        tree = self._schema_base_tree

        # locate the various values provided for vocabularies and create a mapping
        sector_vocab_uuids = dict()
        sectors = dataset.xml_tree.findall('//sector')
        for sector in sectors:
            try:
                vocab = sector.attrib['vocabulary']
            except KeyError:
                continue
            sector_vocab_uuids[vocab] = uuid.uuid4().hex

        # duplicate schema sector elements for each vocab value
        sector_xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector' + '"]')
        schema_sector = tree.getroot().find(sector_xpath)
        for vocab, new_uuid in sector_vocab_uuids.items():
            new_schema_sector = copy.deepcopy(schema_sector)
            new_schema_sector.attrib['name'] = 'sector-' + new_uuid
            tree.getroot().append(new_schema_sector)

        # modify dataset elements to refer to new sector element names
        sector_xpath = '//sector[@vocabulary="{0}"]'
        for vocab, new_uuid in sector_vocab_uuids.items():
            sector_el = dataset.xml_tree.find(sector_xpath.format(vocab))
            # for sector_el in sectors_with_vocab:
            sector_el.tag = 'sector-' + new_uuid

        if len(self.codelists):
            for codelist in self.codelists:
                if codelist.name == 'Version':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'iati-activities' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="version"]')
                elif codelist.name == 'OrganisationType':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'reporting-org' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="type"]')
                elif codelist.name == 'Sector':
                    xpath_default = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="code"]')
                    try:
                        xpath_explicit = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector-' + sector_vocab_uuids['1'] + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="code"]')
                        xpath = xpath_explicit
                    except KeyError:
                        xpath = xpath_default

                elif codelist.name == 'SectorCategory':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector-' + sector_vocab_uuids['2'] + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="code"]')

                elif codelist.name == 'SectorVocabulary':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="vocabulary"]')
                    vocab = get_sector_vocab(dataset)
                    if vocab == '99':
                        try:
                            vocab_uri = dataset.xml_tree.find('//iati-activity/sector').get('vocabulary-uri')

                        except Exception as e:  # TODO: Use a less general exception
                            # cannot find @vocabulary-uri, so perform no checks
                            continue

                        if vocab_uri is None:
                            continue

                        # TODO Fetch user-defined codelist
                        # TODO Parse user-defined codelist
                        # TODO Set user_defined_cl as the parsed codelist
                        user_defined_cl = iati.core.default.codelists()['Sector']
                        codelist = user_defined_cl

                        # At this point, the vocab used is a valid value (i.e. '99'). There is a user-defined codelist that requires validation against. As such, the xpath for @code needs to be set for further validation
                        xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="code"]')

                else:
                    return False

                el_to_update = tree.getroot().find(xpath)
                el_to_update.attrib['type'] = '{0}-type'.format(codelist.name)

                tree.getroot().append(codelist.xsd_tree())

            try:
                return iati.core.utilities.convert_tree_to_schema(tree)
            except etree.XMLSchemaParseError as err:
                iati.core.utilities.log_error(err)
        else:
            return iati.core.utilities.convert_tree_to_schema(tree)
