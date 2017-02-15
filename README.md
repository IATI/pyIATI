# iati.core

The iati.core Python module.

[![Build Status](https://travis-ci.com/IATI/iati.core.svg?token=jGz3fUUcXxQNh1U6Jsyp&branch=master)](https://travis-ci.com/IATI/iati.core)

Varying between: [![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges) and [![unstable](http://badges.github.io/stability-badges/dist/unstable.svg)](http://github.com/badges/stability-badges) (see docstrings)

General Information
===================

This is a Python module containing IATI functionality that would otherwise be replicated in many different locations by many different software projects.

The contents of this library is at best unstable, and much is experimental. As such, it must be expected that its contents and API will change over the short-to-medium term future. `Warning` sections in docstrings help flag up some particular known stability concerns. `Todo` sections describe known missing or incorrect features.

**Feedback, suggestions, use-case descriptions, bug reports and so on are much appreciated** - it's far better to know of issues earlier in the development cycle.

At present the library (`core`) represents the contents of the [IATI Single Source of Truth(SSOT)](https://github.com/iati/iati-standard-ssot). It is able to handle a single version of the Standard (2.02 by default, although it is possible to change data files). Some placeholder work has been undertaken to deal with multiple standard versions. It is planned that this work will be completed once surrounding APIs are nearer a stable state.

More pleasant API naming, better hiding of underlying `lxml`, full documentation, improved error handling, and a greater number of tests for edge-cases are known key areas for improvement.

It is planned that different sections of the library, such as `validate` are split into their own repositories. They exist within this repository at present to help speed up the iteration process.

General Installation for System Use
===================================

```
# install software dependencies
apt-get install python-pip

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
```

Alternatively, the Makefile can be used.

```
make tests
make lint
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
