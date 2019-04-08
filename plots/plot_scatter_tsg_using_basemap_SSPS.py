from netCDF4 import Dataset
import numpy as np
#import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import csv
from mpl_toolkits.basemap import Basemap

file = 'OS_PIRATA-FR29_TSG.nc'
ncpath = '.'
path = 'png'

ncfile = os.path.join(ncpath, file)
nc = Dataset(ncfile, mode='r')

SSPS = nc.variables['SSPS']
SSTP = nc.variables['SSTP']
TIME = nc.variables['TIME']
LATITUDE = nc.variables['LATITUDE']
LONGITUDE = nc.variables['LONGITUDE']
CM = nc.cycle_mesure

plt.title('{} - {}'.format(CM, SSPS.long_name))
plt.ylabel('{} '.format(LATITUDE.standard_name), labelpad=30)
plt.xlabel('{} '.format(LONGITUDE.standard_name), labelpad=20)
# setup mercator map projection.
m = Basemap(llcrnrlon=-30.,llcrnrlat=-12.,urcrnrlon=15.,urcrnrlat=19.,\
            rsphere=(6378137.00,6356752.3142),\
            resolution='l',projection='merc',\
            lat_0=40.,lon_0=-20.,lat_ts=20.)
m.drawcoastlines()
m.fillcontinents()
# draw parallels
m.drawparallels(np.arange(-90,90,6),labels=[1,1,0,1])
# draw meridians
m.drawmeridians(np.arange(-180,180,8),labels=[1,1,0,1])
x, y = m(LONGITUDE[:], LATITUDE[:])
plt.scatter(x, y, c=SSPS[:], s=30, cmap='jet', vmin=32, vmax=37)
plt.colorbar(orientation='vertical', shrink=0.8, aspect=20, fraction=0.05,pad=0.12)
figname = '{}_TSG_COLCOR_SCATTER_{}.png'.format(CM, SSPS.standard_name)
dest = os.path.join(path, figname)
plt.savefig(dest)
print('Printing: ', dest)

#plt.show()
plt.cla()