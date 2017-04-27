"""A module containing a core representation of IATI Schemas."""
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

    def _change_include_to_xinclude(self):
        """Change the method in which common elements are included.

        lxml does not contain functionality to access elements within imports defined along the lines of: `<xsd:include schemaLocation="NAME.xsd" />`
        It does, however, contains functionality to access elements within imports defined along the lines of: `<xi:include href="NAME.xsd" parse="xml" />`
        when there is a namespace defined against the root schema element as `xmlns:xi="http://www.w3.org/2001/XInclude"`

        This changes instances of the former to the latter.

        Todo:
            Check whether this is safe in the general case, so allowing it to be performed in __init__().
        """
        # add the namespace
        self._schema_base_tree.getroot().nsmap['xi'] = 'http://www.w3.org/2001/XInclude'
        # import pdb;pdb.set_trace()

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
                except Exception as e:  # TODO: Use a less general exception
                    # cannot find @vocabulary, so use default vocab
                    vocab = '1'
            else:
                # TODO: Raise TypeError
                pass

            return vocab

        # tree = copy.deepcopy(self._schema_base_tree)
        tree = self._schema_base_tree

        if len(self.codelists):
            for codelist in self.codelists:
                if codelist.name == 'Version':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'iati-activities' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="version"]')
                elif codelist.name == 'OrganisationType':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'reporting-org' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="type"]')
                    # import pdb;pdb.set_trace()
                elif codelist.name == 'Sector' or codelist.name == 'SectorCategory':
                    xpath = (iati.core.constants.NAMESPACE + 'element[@name="' + 'sector' + '"]//' + iati.core.constants.NAMESPACE + 'attribute[@name="code"]')
                    vocab = get_sector_vocab(dataset)

                    if codelist.name == 'Sector' and vocab is not '1':
                        # The Sector codelist is only used when a @vocabulary of "1" is used
                        continue
                    if codelist.name == 'SectorCategory' and vocab is not '2':
                        # The SectorCategory codelist is only used when a @vocabulary of "2" is used
                        continue

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
