# oceano2python

This program read ASCII file(s) from oceanographic instruments (Seabird CTD, Sippican XBT, RDI LADCP, etc), extract data from header files and write result into one ASCII and NetCDF OceanSITES file.
Work in progress.

## Installation from scratch with conda

The program works under Windows (terminal) or Git bash as well as under Linux. It is recommended to install miniconda and to create a virtual environment oceano2python.

``` bash
conda create -n oceano2python python=3.9
conda activate oceano2python
conda install -c conda-forge netCDF4 toml matplotlib xarray seawater PyInstaller pysimplegui
pip install julian
```

## Create an environment based on an YAML environment file

``` bash
conda env create -f environment.yml -n <new_env_name>
```

## Export your environment

Duplicate your environment on another machine, just export it to a YAML file:

``` bash
conda env export > environment.yml
```

## Build and run

To build, run tests, build (compiled version), test examples (CTD/XBT), with GUI, you can use make:

``` bash
make test
make build
make ctd
make xbt
make ladcp
make ctd GUI=-g
```

## Usage

By default, the program uses the configuration file under: tests/test.toml, should change in future versions.

``` bash
python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD 
python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -c <config.toml> -i CTD -d
python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS
python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -d
python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL
python oceano.py data/LADCP/*.lad - i LADCP - k DEPTH EWCT NSCT
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
