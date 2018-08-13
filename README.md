# pyIATI

A developers’ toolkit for IATI.

[![Build Status](https://travis-ci.org/IATI/pyIATI.svg?branch=master)](https://travis-ci.org/IATI/pyIATI) [![PyPI](https://img.shields.io/pypi/v/pyIATI.svg)](https://pypi.python.org/pypi/pyIATI)

`master`: [![Requirements Status](https://requires.io/github/IATI/pyIATI/requirements.svg?branch=master)](https://requires.io/github/IATI/pyIATI/requirements/?branch=master) `dev`: [![Requirements Status](https://requires.io/github/IATI/pyIATI/requirements.svg?branch=dev)](https://requires.io/github/IATI/pyIATI/requirements/?branch=dev)

Varying between: ![experimental](https://img.shields.io/badge/stability-experimental-orange.svg) and ![unstable](https://img.shields.io/badge/stability-unstable-yellow.svg) (see docstrings)

General Information
===================

This is a Python module containing IATI functionality that would otherwise be replicated in many different locations by many different software projects.

**The contents of this library is at best unstable, and much is experimental**. As such, it must be expected that its contents and API will change over the short-to-medium term future. `Warning` sections in docstrings help flag up some particular known stability concerns. `Todo` sections describe known missing or incorrect features.

**Feedback, suggestions, use-case descriptions, bug reports and so on are much appreciated** - it's far better to know of issues earlier in the development cycle. Please use [Github Issues](https://github.com/IATI/iati.core/issues) for this.

At present the library (`core`) represents much of the contents of the [IATI Single Source of Truth (SSOT)](https://github.com/iati/iati-standard-ssot).

More pleasant API naming, better hiding of underlying `lxml`, full documentation, improved error handling, and a greater number of tests for edge-cases are known key areas for improvement.


General Installation for System Use
===================================

```shell
# install software dependencies
apt-get install python-pip libxml2-dev libxslt-dev python-dev pandoc

# install this package
pip install pyIATI
```

Documentation
=============

The docs are not currently hosted and must be locally generated. To do this you must first:

1. Clone this repo.
2. Create a new virtualenv using at least python3.5+
3. `pip install -r requirements_dev.txt`

At present, an HTML documentation site can be generated using the following commands:

```shell
# to build the documentation
cd pyIATI
make -B docs
open docs/build/index.html # for Mac OS
xdg-open docs/build/index.html # for linux
```

IATI Version Support
====================

pyIATI fully supports versions `1.04`, `1.05`, `2.01`, `2.02` and `2.03` of the IATI Standard.

Schemas for versions `1.01`, `1.02` and `1.03` are included in the `iati/resources/standard` directory but are not yet accessible using the available pyIATI functions to return default schemas.


Usage
=====

**WARNING:** This library is currently in active development. **All usage examples are subject to change**, as we iteratively improve functionality. Therefore, the following examples are provided for illustrative purposes only. As the library matures, this message and other documentation will be updated accordingly.

Once installed, the library provides functionality to represent IATI Schemas, Codelists and publisher datasets as Python objects. The IATI Standard schemas and codelists are provided out of the box (using `iati.default`), however this can be manipulated if bespoke versions of the Schemas/Codelists are required.

### Loading an XSD Schema

A number of default IATI `.xsd` schema files are included as part of the library. They are stored in the folder: `iati.core/iati/core/resources/schemas/`

The following example loads the latest IATI Activity Schema:

```python
import iati.default
schema = iati.default.activity_schema('2.03')
```

By default, the default Schema will be populated with other information such as Codelists and Rulesets for the specified version of the Standard.

To access an Organisation Schema for version 1.05, with no additional information added:

```python
import iati.default
schema = iati.default.organisation_schema('1.05', False)
```

Helper functions will be written in due course to return all XPaths within a Schema, as well as documentation for each element. Work in this area can be seen in the `get-data-from-schema` branch.

### Loading Codelists

A given IATI Codelist can be added to a Schema. Example using the [Country](http://iatistandard.org/codelists/Country/) codelist.

```python
import iati.default
country_codelist = iati.default.codelist('Country', '2.03')
schema.codelists.add(country_codelist)
```

All Codelists for the latest version of the Standard can be accessed with:

```python
import iati.default
all_latest_codelists = iati.default.codelists('2.03'):
```

### Loading Rulesets

The default IATI Ruleset can be loaded by using:

```python
import iati.default
iati.default.ruleset('2.03')
```

If you wish to load your own Ruleset you can do this using:

```python
import iati.rulesets
import iati.utilities

# Load a local Ruleset
ruleset_str = iati.utilities.load_as_string('/absolute/path/to/ruleset.json')

# To create a Ruleset object from your ruleset_str:
iati.Ruleset(ruleset_str)
```

### Working with IATI Datasets

#### Loading a dataset - local

```python
import iati.utilities

# Load a local file
dataset = iati.utilities.load_as_dataset('/absolute/path/to/iati-activites.xml')
```

#### Loading a dataset - remote

This functionality converts XML strings into bytes and passes it through some internal validation using lxml. Because of this Unicode strings with encoding declaration cannot be instantiated without additional steps as Datasets at this time. See: [Python Unicode Strings](https://lxml.de/parsing.html#python-unicode-strings) for more information.

```python
import iati.data

# Load a remote file
# Assumes the Requests library is installed: http://docs.python-requests.org/
import requests
dataset_as_string = requests.get('http://XML_FILE_URL_HERE').text

dataset = iati.Dataset(dataset_as_string)
```


### Validating datasets

A `Dataset` object can be validated for adherence to XML and/or the IATI schemas. IATI schemas can be verified using methods in `iati.validator`.

#### Simple validation

Returns a number of booleans:

```python
import iati.default
import iati.validator

# Set-up a sample dataset and get the default v2.03 schema
>>> dataset = iati.Dataset("""
... <iati-activities version="2.03">
...   <iati-activity>
...   </iati-activity>
... </iati-activities>
... """)  # This dataset is XML, but not IATI XML as it's missing mandatory elements.
>>> v203_schema = iati.default.activity_schema('2.03')

# Check whether the dataset is valid XML.
>>> iati.validator.is_xml(dataset)
True

# Check whether the dataset is valid IATI XML according to the 2.03 schema version.
>>> iati.validator.is_iati_xml(dataset, v203_schema)
False

# Check whether the dataset is valid according to the 2.03 IATI schema and ruleset.
>>> iati.validator.is_valid(dataset, v203_schema)
False
```

#### Detailed validation

Datasets can be validated to return a `ValidationErrorLog`. This can be performed using:

```python
import iati.default
import iati.validator

# Set-up a sample dataset and get the default v2.03 schema
>>> dataset = iati.Dataset("""
... <iati-activities version="2.03">
...   <iati-activity>
...   </iati-activity>
... </iati-activities>
... """)  # This dataset is XML, but not IATI XML as it's missing mandatory elements.
>>> v203_schema = iati.default.activity_schema('2.03')

# Check whether the dataset is valid XML. Returns a ValidationErrorLog object.
>>> error_log = iati.validator.full_validation(dataset, v203_schema)

# The error log can be read using the following:
>>> len(error_log)  # Number of errors or warnings found
25

>>> error_log.contains_errors()  # Boolean value returned if at least one error is present
True

>>> error_log.contains_warnings() # Boolean value returned if at least one warning is present
True

# A breakdown of the first error found:
>>> first_error = error_log[0]
>>> first_error.info
"<string>:2:0:ERROR:SCHEMASV:SCHEMAV_ELEMENT_CONTENT: Element 'iati-activity': Missing child element(s). Expected is ( iati-identifier )."

>>> first_error.description
'A different element was found than was expected.'

>>> first_error.help
'There are a number of mandatory elements that an IATI data file must contain. Additionally, these must occur in the required order.\nFor more information about what an XML element is, see https://www.w3schools.com/xml/xml_elements.asp'

>>> first_error.status
'error'

>>> first_error.name
'err-not-iati-xml-missing-required-element'

```


#### Accessing data

The `Dataset` object contains an `xml_tree` attribute (itself an `lxml.etree` object). [XPath expessions](https://www.w3schools.com/xml/xpath_intro.asp) can be used to extract desired information from the dataset. For example:

```python
# WARNING: The following examples assume the source dataset file is produced in IATI v2.x format

# Show the activities contained within the dataset
> dataset.xml_tree.xpath('iati-activity')
[<Element iati-activity at 0x2c5a5f0>, <Element iati-activity at 0x2c5ac68>, <Element iati-activity at 0x2c5acf8>, <Element iati-activity at 0x2c5ad40>]

# Show the title for each project
> dataset.xml_tree.xpath('iati-activity/title/narrative/text()')
['\nIMPROVING MATERNAL HEALTH AND REDUCING CHILD MORTALITY THROUGH DEVELOPING HEALTH SERVICE DELIVERY FOR THE POOR AND MARGINALISED COMMUNITY OF BAGHBANAN, NORTH WEST PAKISTAN\n', '\nIMPROVING MATERNAL HEALTH AND REDUCING CHILD MORTALITY THROUGH DEVELOPING HEALTH SERVICE DELIVERY FOR THE POOR AND MARGINALISED COMMUNITY OF BAGHBANAN, NORTH WEST PAKISTAN\n', '\nImproving maternal health and reducing child mortality through developing health service delivery for the poor and marginalised community in Baghbanan, North West Pakistan\n', '\nIMPROVED HEALTH SERVICE DELIVERY IN NORTH WEST PAKISTAN (\n']

# For the first activity only, show the planned start date (i.e. activity date type = 2)
> dataset.xml_tree.xpath('iati-activity[1]/activity-date[@type=2]/@iso-date')
['2014-01-01']
```


Python Version Support
======================

This code supports Python 2.7 and 3.4+. We advise use of Python 3.5 (or above) as these versions of the language provide some rather useful features that will likely be integrated into this codebase.


Dev Installation
================

```shell
# install software development dependencies
apt-get install python-pip python-virtualenv

# create and start a virtual environment
virtualenv -p python3 pyenv
source pyenv/bin/activate

# install Python package dependencies
pip install -r requirements_dev.txt
```


Tests
=====

```shell
# to run the tests
py.test iati/

# to run the linters
pylint iati
flake8 iati/
pydocstyle iati/
# OR
pylint iati; echo; flake8 iati/; echo; pydocstyle iati/

# to run the complexity and maintainability checks
radon mi iati/ -nb
radon cc iati --no-assert -nc
```

Alternatively, the Makefile can be used.

```
make test
make lint
make complexity
make docs

# OR

make all
```


Licensing
=========

This software is available under the MIT License (see `LICENSE.txt`), and utilises third party libraries and tools that are distributed under their own terms (see `LICENSE-3RD-PARTY.txt`). Details of the authors of this software are provided in `AUTHORS.txt`.
