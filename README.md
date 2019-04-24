# oceano2python

This program read ASCII file(s) from oceanographic instruments (Seabird CTD, Sippican XBT, RDI LADCP, etc), extract data from header files and write result into one ASCII and NetCDF OceanSITES file.
Work in progress.

## dev

We use Visual Studio Code (VSC)

## prequisite

You need to install aditional Python packages for the following OS:

* [Windows](https://github.com/jgrelet/oceano2python/blob/master/INSTALL_WINDOWS.md)
* [Linux](https://github.com/jgrelet/oceano2python/blob/master/INSTALL_LINUX.md)

## build and run

To build, run and test, you can use make:

``` bash
make build
make test
make run
```