# folders
DOCS_FOLDER = docs
DOCS_FOLDER_BUILD = $(DOCS_FOLDER)/build/
DOCS_FOLDER_SOURCE = $(DOCS_FOLDER)/source/
IATI_FOLDER = iati/

# useful constants
LINE_SEP = ---

all: test lint docs


docs: $(IATI_FOLDER) $(DOCS_FOLDER_SOURCE)
	sphinx-apidoc -f -o $(DOCS_FOLDER_SOURCE) $(IATI_FOLDER)
	echo $(LINE_SEP)
	sphinx-build -b html $(DOCS_FOLDER_SOURCE) $(DOCS_FOLDER_BUILD)


lint: $(IATI_FOLDER)
	-pylint $(IATI_FOLDER)
	echo $(LINE_SEP)
	-flake8 $(IATI_FOLDER)
	echo $(LINE_SEP)
	pydocstyle $(IATI_FOLDER)
	echo $(LINE_SEP)
	radon mi $(IATI_FOLDER) -nb


test: $(IATI_FOLDER)
	py.test --cov-report term-missing:skip-covered --cov=$(IATI_FOLDER) $(IATI_FOLDER)
