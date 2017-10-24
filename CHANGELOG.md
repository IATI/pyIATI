# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

- [Deployment] Include resource data in package distribution [#195].

### Security

## [0.1.0] - 2017-10-19

### Added

- [Codelists] Blank Codelists may be created and given a name.
- [Codelists] Codelists may be created from a string conforming to the Codelist Schema.
- [Codelists] Codelists contain a set of Codes.
- [Codelists] Codelists may be output as a XSD simpleType restriction containing enumeration elements.
- [Codelists] Codelist equality is based on whether the names and contained Codes are the same.
- [Codelists] Codes may be created from an optional value and name.
- [Codelists] Codes may be output as a XSD enumeration to be contained within a simpleType restriction.
- [Codelists] Code equality is determined based on whether name and value are the same.

- [Constants] A number of constants are defined, though should be deemed private to the library.

- [Datasets] Datasets can represent each Activity and Organisation files (though not at the same time!).
- [Datasets] A Dataset may be created either from a string or a lxml ElementTree.
- [Datasets] The contents of a Dataset can be accessed as each a string and an ElementTree. These values remain in sync with each other.
- [Datasets] The version of the IATI Standard at which a Dataset is defined can be obtained through the `version` property.
- [Datasets] Subsections of a Dataset (indexed by line number) may be obtained in string format.

- [Defaults] The `defaults` module provides access to the contents of the SSOT.
- [Defaults] To obtain SSOT contents, the desired version of the Standard must be specified. Should a version not be specified, the latest version will be assumed.
- [Defaults] Specific Codelists from the SSOT may be accessed by name.
- [Defaults] All Codelists from the SSOT may be accessed at once. No differentiation is made between Embedded and Non-Embedded Codelists.
- [Defaults] The Standard Ruleset may be accessed.
- [Defaults] The Ruleset Schema may be accessed. *NOTE:* This is a JSON (dict) object, not an `iati.Schema`.
- [Defaults] The Activity Schema may be accessed.
- [Defaults] The Organisation Schema may be accessed.
- [Defaults] By default, the Activity and Organisation Schemas will be populated with all the Codelists and Rulesets at the desired version of the Standard.
- [Defaults] Unpopulated Activity and Organisation Schemas may be accessed by overriding a default argument.

- [Exceptions] There is very rudimentary exception handling.
- [Exceptions] Some exceptions are logged.
- [Exceptions] Some raised exceptions have descriptions to make it possible to consistently determine the cause.

- [Resources] Resources are static files that come with the library, split into 'The Standard' and 'Test Data'.
- [Resources] Resources are stored and accessed based on a particular Decimal Version.
- [Resources] Schemas, Codelists and Rulesets are available for V1.04-2.02.
- [Resources] Schemas are available for V1.03 and prior.
- [Resources] Non-embedded Codelists are deemed to have a single form valid for V1.04-2.02.
- [Resources] Schema test data from the SSOT is present for V1.01-2.02.
- [Resources] Custom test data has been created for V2.02.
- [Resources] Resources may be loaded from disk as bytes, a Dataset, a string or an ElementTree.

- [Rulesets] Blank Rulesets may be created by providing no arguments.
- [Rulesets] Rulesets may be created from a string conforming to the Ruleset Schema.
- [Rulesets] Rulesets contain a set of Rules.
- [Rulesets] A Dataset may have truthy conformance checked against a Ruleset.
- [Rulesets] Rules may be created from a `context` and a `case`.
- [Rulesets] Each of the Rules in the Ruleset Schema have been implemented for instantiation and truthy conformance. These are: atleast_one, date_order, dependent, no_more_than_one, regex_matches, regex_no_matches, startswith, sum, unique
- [Rulesets] A Rule base class exists to allow the creation of custom types of Rule.
- [Rulesets] The string representation of a Rule details what must occur for a Dataset to be conformant.
- [Rulesets] A Dataset may have truthy conformance checked against a Rule. NOTE: A Rule may skip or raise an error.

- [Schemas] Schemas may be created by providing a path to a file containing a valid XSD.
- [Schemas] Schemas contain a set of Codelists.
- [Schemas] Schemas contain a set of Rulesets.
- [Schemas] Should a XSD be defined across multiple files, the resulting Schema shall be flattened to allow programmatic access to all of its contents.
- [Schemas] Activity and Organisation Schemas have been implemented.

- [Utility] A new namespace may be added to a Schema.
- [Utility] There is a function to convert from ElementTree to XMLSchema.
- [Utility] There is a function to convert from a string to an ElementTree.
- [Utility] There is a function to work around RFC4627 by preventing duplicate keys in a JSON file.
- [Utility] There is very rudimentary logging functionality.
- [Utility] Various functionality to access Version Numbers is present.

- [Compatibility] Compatible with Python 2.7, 3.4, 3.5 and 3.6.

- [Tests] All code is comprehensively unit tested.
- [Tests] Datasets, Rulesets, and other components permitting user-defined input tested with range of valid and invalid data.
- [Tests] Variety of never-before-seen edge-cases tested for correct behavior.
- [Tests] Rudimentary custom fuzzing used to ensure expected errors are raised.

- [Tools] Documentation is generated with Sphinx, based on Google-style docstrings.
- [Tools] Documentation is presented using the Sphinx Read the Docs theme.
- [Tools] Linting performed with pylint, flake8 and pydocstyle.
- [Tools] Linters are configured to generally follow PEP8 and PEP257, with a few custom modifications such as line length.
- [Tools] Code complexity is assessed using radon.
- [Tools] Unit testing is performed with pytest.
- [Tools] Full testing is performed by Travis.
- [Tools] Python 2.7 compatibility is provided by both `future` and `six`. Where a custom workaround is used rather than one of these, `python2/3` is present in a comment.

- [XML] lxml utilised for XML functionality.
- [XML] Support XML 1.0.
- [XML] Support XMLSchema 1.0.
- [XML] Support XPath 1.0.
