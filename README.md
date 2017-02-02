# iati.core

The iati.core Python module.

[![Build Status](https://travis-ci.com/IATI/iati.core.svg?token=jGz3fUUcXxQNh1U6Jsyp&branch=master)](https://travis-ci.com/IATI/iati.core)

General Installation for System Use
===================================

```
# install software dependencies
apt-get install python-pip

# install Python package dependencies
pip install -r requirements.txt
```

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

Running
=======

```
# to run the tests
py.test iati/

# to run the linters
pylint iati
flake8 iati/
pydocstyle iati/
# OR
pylint iati; echo; flake8 iati/; echo; pydocstyle iati/

# to build the documentation
sphinx-apidoc -f -o docs/source/ iati/
sphinx-build -b html docs/source/ docs/build/
```

Alternatively, the Makefile can be used.

```
make tests
make lint
make docs

# OR

make all
```
