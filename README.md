# iati.core

The iati.core Python module.

Dev Installation
================

```
# install software development dependencies
apt-get install python-pip python-virtualenv

# create and start a virtual environment
virtualenv -p python3 pyenv
source pyenv/bin/activate

# install Python package dependencies
pip install -r requirements.txt
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
sphinx-apidoc -o docs/source/ iati/
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
