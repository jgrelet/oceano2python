PROJECT = oceano
MAIN = $(PROJECT).py
PYTHON = python
PYLINT = pylint
TEST_PATH = tests
OPTIONS_CTD = data/CTD/cnv/dfr2900?.cnv -i CTD -k PRES ETDD TEMP PSAL DOX2 DENS SVEL FLU2 FLU3 TUR3 NAVG
OPTIONS_XBT = data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL
OPTIONS_LADCP = data/LADCP/*.lad -i LADCP -k DEPTH EWCT NSCT
OPTIONS_BTL =  data/CTD/btl/fr290*.btl -i BTL -k PRES DEPTH ETDD TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2

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

# to run program in GUI mode : make ctd OPT=-g
# to run program in debug mode : make ctd OPT=-d
ctd:
	$(PYTHON) $(MAIN) $(OPTIONS_CTD) $(OPT)

xbt:
	$(PYTHON) $(MAIN) $(OPTIONS_XBT) $(OPT)

ladcp:
	$(PYTHON) $(MAIN) $(OPTIONS_LADCP) $(OPT)

btl:
	$(PYTHON) $(MAIN) $(OPTIONS_BTL) $(OPT)

build:
	pyinstaller -wF --clean $(MAIN)

runc:
	dist/$(PROJECT)
