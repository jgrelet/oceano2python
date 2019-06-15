from netCDF4 import Dataset
import numpy as np
#import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import csv
from mpl_toolkits.basemap import Basemap


file = 'OS_SEAMOUNT02_TSG.nc'
ncpath = '../netcdf/'
path = ''
latmin = -25.
latmax = -20.
lat_ticks = 1
lonmin = 165.
lonmax = 170.
lon_ticks = 1
# resolution to use. Can be c (crude), l (low), i (intermediate), h (high), f (full) or None
resolution = 'i'
minvalue = 22
maxvalue = 25

ncfile = os.path.join(ncpath, file)
nc = Dataset(ncfile, mode='r')

SSPS = nc.variables['SSPS']
SSTP = nc.variables['SSTP']
TIME = nc.variables['TIME']
LATITUDE = nc.variables['LATITUDE']
LONGITUDE = nc.variables['LONGITUDE']
CM = nc.cycle_mesure

plt.title('{}\n{} ({})'.format(CM, SSTP.name, SSTP.long_name))
plt.ylabel('{} '.format(LATITUDE.standard_name), labelpad=30)
plt.xlabel('{} '.format(LONGITUDE.standard_name), labelpad=20)
# setup mercator map projection.
m = Basemap(llcrnrlon = lonmin, llcrnrlat = latmin, urcrnrlon = lonmax, urcrnrlat = latmax,\
            rsphere=(6378137.00,6356752.3142),\
            resolution = resolution, projection='merc')
            #lat_0=40.,lon_0=-20.,lat_ts=20.)
m.drawcoastlines()
m.fillcontinents()
# draw parallels
m.drawparallels(np.arange(-90, 90, lat_ticks),labels=[1,1,0,1])
# draw meridians
m.drawmeridians(np.arange(-180, 180, lon_ticks),labels=[1,1,0,1])
x, y = m(LONGITUDE[:], LATITUDE[:])
plt.scatter(x, y, c=SSTP[:], s=30, cmap='jet', vmin = minvalue, vmax = maxvalue)
plt.colorbar(orientation='vertical', shrink=0.8, aspect=20, fraction=0.05,pad=0.12)
figname = '{}_TSG_COLCOR_SCATTER_{}.png'.format(CM, SSTP.standard_name)
dest = os.path.join(path, figname)
plt.savefig(dest)
print('Printing: ', dest)

#plt.show()
plt.cla()