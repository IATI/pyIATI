# iati.core

The iati.core Python module.

[![Build Status](https://travis-ci.org/IATI/iati.core.svg?branch=master)](https://travis-ci.com/IATI/iati.core) [![Requirements Status](https://requires.io/github/IATI/iati.core/requirements.svg?branch=master)](https://requires.io/github/IATI/iati.core/requirements/?branch=master)

Varying between: [![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges) and [![unstable](http://badges.github.io/stability-badges/dist/unstable.svg)](http://github.com/badges/stability-badges) (see docstrings)

General Information
===================

This is a Python module containing IATI functionality that would otherwise be replicated in many different locations by many different software projects.

**The contents of this library is at best unstable, and much is experimental**. As such, it must be expected that its contents and API will change over the short-to-medium term future. `Warning` sections in docstrings help flag up some particular known stability concerns. `Todo` sections describe known missing or incorrect features.

**Feedback, suggestions, use-case descriptions, bug reports and so on are much appreciated** - it's far better to know of issues earlier in the development cycle. Please use [Github Issues](https://github.com/IATI/iati.core/issues) for this.

At present the library (`core`) represents the contents of the [IATI Single Source of Truth (SSOT)](https://github.com/iati/iati-standard-ssot). It is able to handle a single version of the Standard (2.02 by default, although it is possible to change data files). Some placeholder work has been undertaken to deal with multiple standard versions. It is planned that this work will be completed once surrounding APIs are nearer a stable state.

More pleasant API naming, better hiding of underlying `lxml`, full documentation, improved error handling, and a greater number of tests for edge-cases are known key areas for improvement.

It is planned that different sections of the library, such as `validate` are split into their own repositories. They exist within this repository at present to help speed up the iteration process.


General Installation for System Use
===================================

```
# install software dependencies
apt-get install python-pip libxml2-dev libxslt-dev python-dev

# install this package
python setup.py install
```

Documentation
=============

At present, an HTML documentation site can be generated using the following commands:

```
# to build the documentation
sphinx-apidoc -f -o docs/source/ iati/
sphinx-build -b html docs/source/ docs/build/
```

The file `docs/build/index.html` serves as the documentation home page.


Usage
=====

**WARNING:** This `iati.core` library is currently in active development. **All usage examples are subject to change**, as we iteratively improve functionality.  Therefore, the following examples are provided for illustrative purposes only.  As the library matures, this message and other documentation will be updated accordingly!

Once installed, the library provides functionality to represent IATI Schemas, Codelists and publisher datasets as Python objects.  The IATI Standard schemas and codelists are provided out of the box, however this can be manipulated if bespoke versions of the Schemas/Codelists are required.

### Loading an XSD Schema

A number of default IATI `.xsd` schema files are included as part of the library. They are stored in the folder: `iati.core/iati/core/resources/schemas/202/`

The following example loads the default IATI v2.02 `iati-activities-schema.xsd` schema:

```
import iati.core.default
schema = iati.core.default.schema('iati-activities-schema')
```

Helper functions will be written in due course to return all xpaths within a schema, as well as documentation for each element.

### Loading codelists

A given IATI codelist can be added to the schema. Example using the [Country](http://iatistandard.org/codelists/Country/) codelist.

```
import iati.core.default
schema.codelists.add(iati.core.default.codelist('Country'))
```

The default collection of IATI codelists can be added using:

```
import iati.core.default
for _, codelist in iati.core.default.codelists().items():
    schema.codelists.add(codelist)
```

### Loading Rulesets

The default IATI Ruleset can be loaded by using:

```
import iati.core.default

iati.core.default.ruleset()
```

If you wish to load your own Ruleset you can do this using:

```
import iati.core.resources
import iati.core.Rulesets

ruleset_str = iati.core.resources.load_as_string(filepath)
# To create a Ruleset object from your ruleset_str:
iati.core.Ruleset(ruleset_str)
```

**Note:** This functionality is not yet implemented.

Validate an IATI Dataset against the Standard Ruleset:

To be added.


### Working with IATI datasets

#### Loading a dataset

```
import iati.core.data

# Load a local file
with open('path/to/iati-activites.xml', 'r') as xml_file_object:
    dataset_as_string = xml_file_object.read()

# Load a remote file
# Assumes the Requests library is installed: http://docs.python-requests.org/
import requests
dataset_as_string = requests.get('http://XML_FILE_URL_HERE').text

dataset = iati.core.Dataset(dataset_as_string)
```

#### Accessing data

The `Dataset` object contains an `xml_tree` attribute (itself an `lxml.etree` object). [XPath expessions](https://www.w3schools.com/xml/xpath_intro.asp) can be used to extract desired information from the dataset.  For example:

```
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

```
# install software development dependencies
apt-get install python-pip python-virtualenv

# create and start a virtual environment
virtualenv -p python3 pyenv
source pyenv/bin/activate

# install Python package dependencies
pip install -r requirements-dev.txt
```


Tests
=====

```
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
make tests
make lint
make complexity
make docs

# OR

make all
```


Overall TODOs
=============

- Clearer Configuration
- Docs
  - Examples
  - Formalise Stability
  - Getting Started Guides
  - Tutorial - example usage
- Error Handling
- Licensing
- Add IATI Standard Rulesets / Rules
- Stablise API
- Add versions of the Standard other than the latest (v2.02)
- Add further tests
- Add error cases
- Potentially look at proper fuzzing


Licensing
=========

This software is available under the MIT License (see `LICENSE.txt`), and utilises third party libraries and tools that are distributed under their own terms (see `LICENSE-3RD-PARTY.txt`). Details of the authors of this software are provided in `AUTHORS.txt`.
