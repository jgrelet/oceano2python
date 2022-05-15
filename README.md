# oceano2python

This program read ASCII file(s) from oceanographic instruments:

- Profile: Seabird CTD or RBR, Bottle, Sippican XBT, RDI LADCP
- Trajectory: Seabird TSG, IFREMER COLCOR (realtime), IFREMER CASINO

and extract data from header files and write result into ASCII and NetCDF OceanSITES files.

The last version use an embedded Sqlite3 database to normalize, save and retreive data from memory.

See the [wiki](https://github.com/jgrelet/oceano2python/wiki) for documentation and technical description


