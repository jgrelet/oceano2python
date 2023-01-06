# oceano2python [![Build Status](https://travis-ci.com/jgrelet/oceano2python.svg?branch=master)](https://app.travis-ci.com/github/jgrelet/oceano2python)

This program read ASCII file(s) from oceanographic instruments:

- Profile: Seabird CTD or RBR, Bottle, Sippican XBT, RDI LADCP
- Trajectory: Seabird [Thermosalinograph](https://www.seabird.com/sbe-21-seacat-thermosalinograph/product?id=60762467702) (TSG), Ifremer COLCOR (realtime), Ifremer ship's log [CASINO+](https://www.flotteoceanographique.fr/en/Facilities/Shipboard-software/Gestion-de-missions-et-des-donnees/TECHSAS/Ship-s-log-CASINO)

and extract data from header files and write result into ASCII, ODV and NetCDF OceanSITES files.

The last version use an embedded Sqlite3 database to normalize, save and retreive data from memory.

See the [wiki](https://github.com/jgrelet/oceano2python/wiki) for documentation and technical description.
