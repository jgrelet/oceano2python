# oceano2python

This program read ASCII file(s) from oceanographic instruments (Seabird CTD, Sippican XBT, RDI LADCP, etc), extract data from header files and write result into one ASCII and NetCDF OceanSITES file.

The last version use an embedded Sqlite3 database to save and retreive data from memory.

## Prequisites for Windows

You must install the following tools:

- Visual Studio Code (<https://code.visualstudio.com/>)
- Git (<https://git-scm.com/downloads>)
- miniconda3 (<https://docs.conda.io/en/latest/miniconda.html>)
- chocolatey (<https://chocolatey.org/install>) and install GNU Make package (<https://community.chocolatey.org/packages/make>)
  
## Installation based on an YAML environment file

``` bash
conda env create -f environment.yml -n <new_env_name>
```

example:

``` bash
conda env create -f environment-windows.yml -n oceano2python
```

## Installation from scratch with conda

The program works under Windows (terminal) or Git bash as well as under Linux. It is recommended to install miniconda and to create a virtual environment oceano2python.

``` bash
conda create -n oceano2python python=3.9
conda activate oceano2python
conda install -c conda-forge netCDF4 toml matplotlib xarray seawater PyInstaller pysimplegui
pip install julian notanorm
```

## Export your environment

Duplicate your environment on another machine, just export it to a YAML file, replace "OS" with linux or windows:

``` bash
conda env export --no-builds > environment-<OS>.yml
```

## Build and run

To build, run tests, build (compiled version), test examples (CTD/XBT), with GUI, you can use make:

``` bash
make test
make build
make ctd
make xbt
make ladcp
make btl
make ctd OPT=-g   
make ctd OPT=-d
```

## Configuration

As the project consists of several files (modules), it is necessary to define the access path to the program in the environment variables PYTHONPATH and PATH. 
For example, under Linux:

**Update your PATH in your ~/.profile as:
 
 ``` bash
 if [ -d "/mnt/c/git/Python/oceano2python" ] ; then
    PATH="/mnt/c/git/Python/oceano2python:$PATH"
fi
```

**Add this line in your ~/.bashrc

  export $PYTHONPATH = /mnt/c/git/Python/oceano2python

## Usage

By default, the program uses the configuration file under: tests/test.toml, should change in future versions.

``` bash
cd /mnt/c/cruises/PIRATA/PIRATA-FR32/data-processing/CTD
oceano.py data/cnv/dfr320*.cnv -c ../config.toml -r ../../local/code_roscop.csv -i CTD -k PRES DEPTH ETDD TEMP PSAL DENS SVEL DOX2 FLU2 FLU3 TUR3 NAVG
oceano.py data/btl/fr320*.btl -c ../config.toml -r ../../local/code_roscop.csv -i BTL  -k PRES DEPTH ETDD TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2

cd /mnt/c/cruises/PIRATA/PIRATA-FR32/data-processing/CELERITE
oceano.py data/XBT*.edf -c ../config.toml -r ../../local/code_roscop.csv -i XBT -k DEPTH TEMP SVEL

cd /mnt/c/cruises/PIRATA/PIRATA-FR32/data-processing/LADCP
oceano.py profiles/*.lad -c ../config.toml -r ../../local/code_roscop.csv -i LADCP -k DEPTH EWCT NSCT
```

This program read multiple ASCII file, extract physical parameter following ROSCOP codification at the given column, fill arrays, write header file.

``` bash
positional arguments:
  files                 ASCII file(s) to parse

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           display debug informations
  --demo [{CTD,XBT,LADCP,TSG}]
                        specify the commande line for instrument, eg CTD, XBT,
                        TSG, LADCP
  -c CONFIG, --config CONFIG
                        toml configuration file, (default: tests/test.toml)
  -i [{CTD,XBT,LADCP,TSG}], --instrument [{CTD,XBT,LADCP,TSG}]
                        specify the instrument that produce files, eg CTD,
                        XBT, TSG, LADCP
  -k KEYS [KEYS ...], --keys KEYS [KEYS ...]
                        display dictionary for key(s), (default: ['PRES',
                        'TEMP', 'PSAL'])
  -g, --gui             use GUI interface
  ```

The user must describe in the TOML configuration file the metadata and the structure of the files to be read, see [tests/test.toml](https://github.com/jgrelet/oceano2python/blob/master/tests/test.toml)

## Developpment tools

We use Visual Studio Code (VSC) with Python, better TOML, markdownlint and makefile extensions

## GUI

If you want use QT instead of Tk, replace in oceano.py:

``` bash
import PySimpleGUI as gs
```

with

``` bash
import PySimpleGUIQt as gs
```
