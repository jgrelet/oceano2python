PROJECT = oceano
MAIN = $(PROJECT).py
PYTHON = python
PYLINT = pylint
TEST_PATH = tests
OPTIONS_CTD = data/CTD/cnv/dfr2900?.cnv -i CTD -k PRES DEPTH ETDD TEMP PSAL DOX2 DENS SVEL FLU2 FLU3 TUR3 NAVG
OPTIONS_XBT = data/XBT/*.EDF -i XBT -k DEPTH TEMP SVEL
OPTIONS_LADCP = data/LADCP/*.lad -i LADCP -k DEPTH EWCT NSCT
OPTIONS_BTL =  data/CTD/btl/fr290*.btl -i BTL -k BOTL ETDD PRES DEPTH TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2
OPTIONS_RBR = data/RBR/fr29*.txt -i RBR -k PRES DEPTH TEMP PSAL DENS SVEL FLU2
OPTIONS_MVP = data/MVP/mvp_*.m1 -i MVP -k PRES DEPTH TEMP PSAL DENS SVEL
OPTIONS_COLCOR = data/TSG/COLCOR/*.COLCOR -i COLCOR -k SSJT SSTP SSPS
OPTIONS_SEASAVE = data/TSG/SEASAVE/*.cnv -i TSG -k ETDD LATITUDE LONGITUDE SSJT SSTP SSPS DENS SVEL
OPTIONS_CASINO = data/CASINO/*.csv -i CASINO -k LATITUDE LONGITUDE SSJT SSTP SSPS WMSP WDIR

.PHONY: clean-pyc clean-build lint test run build

clean-all: clean-pyc clean-build

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

all: ctd xbt ladcp btl rbr colcor casino

# to run program in debug mode : make ctd OPT=-d
ctd:
	$(PYTHON) $(MAIN) $(OPTIONS_CTD) $(OPT)

xbt:
	$(PYTHON) $(MAIN) $(OPTIONS_XBT) $(OPT)

ladcp:
	$(PYTHON) $(MAIN) $(OPTIONS_LADCP) $(OPT)

btl:
	$(PYTHON) $(MAIN) $(OPTIONS_BTL) $(OPT)

rbr :
	$(PYTHON) $(MAIN) $(OPTIONS_RBR) $(OPT)

mvp :
	$(PYTHON) $(MAIN) $(OPTIONS_MVP) $(OPT)
	
colcor:
	$(PYTHON) $(MAIN) $(OPTIONS_COLCOR) $(OPT)

tsg:
	$(PYTHON) $(MAIN) $(OPTIONS_SEASAVE) $(OPT)

casino:
	$(PYTHON) $(MAIN) $(OPTIONS_CASINO) $(OPT)

build:
	pyinstaller -wF --clean $(MAIN)

runc:
	dist/$(PROJECT)
