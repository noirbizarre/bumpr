BASEDIR=$(CURDIR)
DOCDIR=$(BASEDIR)/doc
DISTDIR=$(BASEDIR)/dist
PACKAGE='bumpr'
PYTHON_VERSION=$(shell python -c 'import sys; print(".".join(str(v) for v in sys.version_info))' | cut -d. -f1,2)

help:
	@echo 'Makefile for Bump\'R'
	@echo '                                                                     '
	@echo 'Usage:                                                               '
	@echo '   make test             Run the test suite                          '
	@echo '   make coverage         Run a coverage report from the test suite   '
	@echo '   make pep8             Run the PEP8 report                         '
	@echo '   make pylint           Run the pylint report                       '
	@echo '   make doc              Generate the documentation                  '
	@echo '   make dist             Generate a distributable package            '
	@echo '   make clean            Remove all temporary and generated artifacts'
	@echo '                                                                     '


test:
	@echo 'Running test suite'
ifeq ($(PYTHON_VERSION),2.6)
	@unit2 discover
else
	@python -m unittest discover
endif

coverage:
	@echo 'Running test suite with coverage'
	@coverage erase
ifeq ($(PYTHON_VERSION),2.6)
	@coverage run --rcfile=coverage.rc -m unittest2 discover
else
	@coverage run --rcfile=coverage.rc -m unittest discover
endif
	@echo
	@coverage report --rcfile=coverage.rc

pep8:
	@pep8 $(PACKAGE) --config=pep8.rc
	@echo 'PEP8: OK'

pylint:
	@pylint --reports=n --rcfile=pylint.rc $(PACKAGE)

doc:
	@echo 'Generating documentation'
	@cd $(DOCDIR) && make html
	@echo 'Done'

dist:
	@echo 'Generating a distributable python package'
	@python setup.py sdist
	@echo 'Done'

clean:
	rm -fr $(DISTDIR)

.PHONY: doc help clean test dists
