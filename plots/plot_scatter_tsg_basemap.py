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
LISTE_VARIABLE_PLOT = ['SSTP', 'SSPS']
plt.cla()
for VAR_A_PLOT in range(len(LISTE_VARIABLE_PLOT)):
    plt.cla()
    INDICE = VAR_A_PLOT

    VAR_A_PLOT = nc.variables[LISTE_VARIABLE_PLOT[VAR_A_PLOT]]
    #SSTP = nc.variables['SSTP']
    TIME = nc.variables['TIME']
    LATITUDE = nc.variables['LATITUDE']
    LONGITUDE = nc.variables['LONGITUDE']
    CM = nc.cycle_mesure
    
    #plt.subplot(111)
    plt.title('{} - {}'.format(CM, VAR_A_PLOT.long_name))
    plt.ylabel('{} '.format(LATITUDE.standard_name), labelpad=30)
    plt.xlabel('{} '.format(LONGITUDE.standard_name), labelpad=20)
    #plt.colorbar(orientation='vertical')
    
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
    #m.set(xlabel='{} '.format(LONGITUDE.standard_name), ylabel='{} '.format(LATITUDE.standard_name),
    #       title='{} - {}'.format(CM, SSPS.long_name))
    
    x, y = m(LONGITUDE[:], LATITUDE[:])

    if INDICE == 0:
        plt.scatter(x, y, c=VAR_A_PLOT[:], s=30, cmap='jet', vmin=21, vmax=32)
    else:
        plt.scatter(x, y, c=VAR_A_PLOT[:], s=30, cmap='jet', vmin=32, vmax=37)

    #plt.colorbar(orientation='vertical')
    figname = '{}_TSG_COLCOR_SCATTER_{}.png'.format(CM, VAR_A_PLOT.standard_name)
    dest = os.path.join(path, figname)
    
    plt.savefig(dest)
    print('Printing: ', dest)

    #plt.show()
    plt.cla()