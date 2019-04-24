PROJECT = oceano
MAIN = $(PROJECT).py
PYTHON = python
PYLINT = pylint
TEST_PATH = tests
OPTIONS = data/CTD/cnv/dfr2900[1-3].cnv -i CTD 

.PHONY: clean-pyc clean-build lint test run build

clean-all:  clean-pyc clean-build

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	
clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive __pycache__/

lint:
	$(PYLINT) --exclude=.tox

test: 
	$(PYTHON) -m unittest  discover -v  $(TEST_PATH)

run:
	$(PYTHON) $(MAIN) $(OPTIONS)

build:
	pyinstaller -wF $(MAIN)

runc:
	dist/$(PROJECT)