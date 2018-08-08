# folders
DOCS_FOLDER = docs
DOCS_FOLDER_BUILD = $(DOCS_FOLDER)/build/
DOCS_FOLDER_SOURCE = $(DOCS_FOLDER)/source/
IATI_FOLDER = iati/

# useful constants
LINE_SEP = ---

all: test lint complexity docs


complexity: $(IATI_FOLDER)
	radon mi $(IATI_FOLDER) -nb
	echo $(LINE_SEP)
	radon cc $(IATI_FOLDER) --no-assert -nc


docs: $(IATI_FOLDER) $(DOCS_FOLDER_SOURCE)
	sphinx-apidoc -f -o $(DOCS_FOLDER_SOURCE) $(IATI_FOLDER) iati/core/tests/* iati/tests/*
	echo $(LINE_SEP)
	sphinx-build -b html $(DOCS_FOLDER_SOURCE) $(DOCS_FOLDER_BUILD)


lint: $(IATI_FOLDER)
	-make pylint
	echo $(LINE_SEP)
	-make flake8
	echo $(LINE_SEP)
	-make pydocstyle


pylint: $(IATI_FOLDER)
	pylint $(IATI_FOLDER)


flake8: $(IATI_FOLDER)
	flake8 $(IATI_FOLDER)


pydocstyle: $(IATI_FOLDER)
	pydocstyle $(IATI_FOLDER)


test: $(IATI_FOLDER)
	py.test --cov-report term-missing:skip-covered --cov=$(IATI_FOLDER) $(IATI_FOLDER)


testp: $(IATI_FOLDER)
	py.test --cov-report term-missing:skip-covered --cov=$(IATI_FOLDER) -n 2 $(IATI_FOLDER)
