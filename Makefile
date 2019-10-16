PROJECT = oceano
MAIN = $(PROJECT).py
PYTHON = python
PYLINT = pylint
TEST_PATH = tests
OPTIONS_CTD = data/CTD/cnv/dfr2900[1-3].cnv -i CTD 
OPTIONS_XBT = data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL

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

# to run program in GUI mode : make ctd GUI=-g
ctd:
	$(PYTHON) $(MAIN) $(OPTIONS_CTD) $(GUI)

# to run program in GUI mode : make xbt GUI=-g
xbt:
	$(PYTHON) $(MAIN) $(OPTIONS_XBT) $(GUI)

build:
	pyinstaller -wF $(MAIN)

runc:
	dist/$(PROJECT)
