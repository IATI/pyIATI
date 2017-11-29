# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- [Datasets] A Dataset `xml_tree` may be set with an ElementTree. [#235]

- [Resources] Updated SSOT to latest content as of 2017-11-14. [#237]
- [Resources] Remove SSOT organisation test files that are not valid XML. [IATI/IATI-Schemas#376, #242]

- [Utility] Non-resource files may be loaded using utility functions. [#235]

- [Schemas] Test that multiple Rulesets can be added to a Schema. [#254]

- [Validation] `full_validation()` now checks whether a Dataset is IATI XML. [#239]
- [Validation] Test that SSOT organisation test files are valid IATI XML. [#242]

### Changed

- [Codelists] `complete` attribute included in equality comparison and hash calculations. [#247]
- [Codelists] Codes must have a value to instantiate. [#247]

- [Resources] Move `load_as_x` functions to `iati.utilities`. [#235]
- [Resources] Rename version-specific resource folders to reduce ambiguity. [#217]
- [Resources] Rename various resource functions to improve clarity. [#259]

- [Rulesets] `validate_ruleset()` changed from public to private function. [#246]
- [Rulesets] `case` attribute on a Rule changed from public to private. [#252]
- [Rulesets] `context` attribute on a Rule changed to read-only property. [#253]

- [Validation] `_check_is_iati_xml()` will raise a `TypeError` when given a non-dataset. This replaces an undocumented `AttributeError`. [#239]

### Deprecated

### Removed

- [Documentation] Stop tracking auto-generated docs templates. [#236]

- [Rulesets] `ruleset` attribute removed from Rulesets. [#246]

- [Tests] `iati.tests.resources.get_test_ruleset_path()` removed due to no calls to function. [#256]

### Fixed

- [Codelists] Fixed impossible XPath in Codelist Mapping File. [IATI/IATI-Codelists#119, #229]
- [Codelists] Sort Codes in a Codelist before hashing so that Codelists with the same Codes always have the same hash. [#247]

- [Defaults] Test and document `ValueError`s that can be raised by functions in `iati.default`. [#241]

- [Rulesets] `name` attribute on a Rule changed to read-only property. [#251]
- [Rulesets] Equal Rulesets are now deemed to be equal. [#249]

- [Validation] Prevent `XPathEvalError`s occurring when given a Codelist Mapping XPath that identifies something other than an attribute. [#229]
- [Validation] Datasets with an `xml:lang` attribute no longer raise a `KeyError` upon performing Codelist validation against a Schema populated with the Language Codelist. [#226]

### Security


## [0.2.0] - 2017-11-07

### Added

- [Codelists] Implement the `complete` attribute. [#45]
- [Codelists] Codes may have equality compared with strings - the `value` of a Code is compared. [#45]
- [Codelists] Add v2.02 Codelist mapping file. [#45]

- [Documentation] Clarify version support in README. [#216]

- [Exceptions] Add an `error_log` attribute to ValidationErrors. [#45]

- [Resources] Add method to load data files relating to pyIATI (rather than the IATI Standard, or tests). [#45]
- [Resources] Allow test files to be located within sub-folders by including slashes (`/`) in the name. [#45]
- [Resources] Detect encoding of files that are not UTF-8. [#45]

- [Validation] Change from `validate.py` to `validator.py` to improve readability of code using this module. [#86]
- [Validation] Add a YAML file containing error information. [#117]
- [Validation] Check whether a string is valid XML - truthy. [#45]
- [Validation] Check whether a string is valid XML - detailed error information. [#45]
- [Validation] Provide custom error messages when lxml returns errors for a string that is not XML. [#90]
- [Validation] Check whether a Dataset is valid against an IATI Schema - truthy. [#45]
- [Validation] Check whether a Dataset is valid against an IATI Schema - detailed error information. [#45]
- [Validation] Provide custom error messages when lxml returns errors for Datasets that do not contain valid IATI XML. [#92]
- [Validation] Check whether attributes in a Dataset have values from Codelists where required - truthy. [#45]
- [Validation] Check whether attributes in a Dataset have values from Codelists where required - detailed error information. [#45]
- [Validation] Check whether a Dataset conforms with Rules in a Ruleset - truthy. [#58]
- [Validation] Check whether a Dataset conforms with Rules in a Ruleset - basic information about which Rules fail. [#58]
- [Validation] Add a `ValidationErrorLog` containing `ValidationError`s to track validation errors. [#87]
- [Validation] Rudimentary differentiation of errors and warnings. [#45]

- [Tests] Add a range of test XML files. [#45]
- [Tests] Add some missing tests. [#45]
- [Tests] Add a somewhat normal-looking string to use for fuzzing. [#113]

### Changed

- [Codelists] The default name for a Code is now an empty string. [#45]
- [Codelists] The name of a Code is no longer included when computing the hash. [#45]

- [Datasets] pyIATI validation functionality used to determine whether a string is XML. This changes the types of Error that may be raised when updating the XML that a Dataset represents. [#95]

- [Tests] Re-organise test data to use folders to separate logical groups. [#58]
- [Tests] Functions for locating and loading test data moved from `iati.resources` and `iati.tests.utilities` to `iati.tests.resources`. [#215]
- [Tests] Re-organise test data to use folders to separate logical groups. [#58]

### Fixed

- [Codelists] The names of Codes are detected in CLv2 XML Codelists (when there are no `<narrative>` elements).

- [Documentation] Corrected some out-of-date documentation. [#45]

- [Rulesets] Update `date_order` XPaths in Standard Ruleset. [IATI/IATI-Rulesets#31]


## [0.1.1] - 2017-10-25

### Fixed

- [Deployment] Include resource data in package distribution [#195].

- [Docs] The README is up-to-date, and so better matches the code. [#198].

### Removed

- [Deployment] Remove attempt at excluding test files from deployed package [#202].


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
