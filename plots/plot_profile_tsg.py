from netCDF4 import Dataset
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
from datetime import date
import datetime
from PyAstronomy import pyasl
from scipy.interpolate import griddata

#change the year for the plot
annee = 2019

# in batch mode, without display
#matplotlib.use('Agg')  

file = 'OS_PIRATA-FR29_TSG.nc'
<<<<<<< HEAD
=======
path_clim = '../climato/'
clim = 'isas13_monthly_surf.nc'
>>>>>>> 0fc9903c756f8ee2046db03512c9fda828b01a9a
ncpath = '.'
path = 'png'

ncfile = os.path.join(ncpath, file)
nc = Dataset(ncfile, mode='r')

SSPS = nc.variables['SSPS']
SSTP = nc.variables['SSTP']
TIME = nc.variables['TIME']
CM = nc.cycle_mesure
LON = nc.variables['LONGITUDE']
LAT = nc.variables['LATITUDE']


#definition of the day for the current year and the start year of netcdf
df = datetime.datetime(annee, 1, 1, 0)
dd = datetime.datetime(1950, 1, 1, 0)
#convert day to julian day real
jul = pyasl.jdcnv(df)
jul2 = pyasl.jdcnv(dd)

#calculation of the current year julian day since the beginig of julian day
DIFF = jul - jul2

#test
#from datetime import datetime
#units=nc.variables['TIME'].units
#buf=nc.variables['TIME']
#TIME=list()
#TIME.extend(buf.tolist())
#dates=nc.num2date(TIME,units,'julian').tolist()

#import julian
#import datetime

#TIME = julian.from_jd(TIME, fmt='mjd')
#end test

#setting of the curent julian day
time = TIME[:] - DIFF

# move subplot outside loop prevent: RuntimeWarning: More than 20 figures have been opened.
fig, ax = plt.subplots(2,1)

fig.set_size_inches(10.5, 8.5, forward=True)

fig.suptitle(CM, fontsize=14, fontweight='bold')

ax[0].plot(time, SSPS, 'r')
ax[0].set_xlabel('Jours Julien')
ax[0].set_ylabel(SSPS.long_name)
ax[0].spines['left'].set_color('red')
ax[0].spines['right'].set_color('red')
ax[0].yaxis.label.set_color('red')
ax[0].tick_params(axis='y', colors='red')

ax[1].plot(time, SSTP, 'g')
ax[1].set_xlabel('Jours Julien')
ax[1].set_ylabel(SSTP.long_name)
ax[1].spines['left'].set_color('green')
ax[1].spines['right'].set_color('green')
ax[1].yaxis.label.set_color('green')
ax[1].tick_params(axis='y', colors='green')

figname = '{}_TSG_COLCOR_SST-SSPS.png'.format(CM)
dest = os.path.join(path, figname)
fig.savefig(dest)
print('Printing: ', dest)
plt.show()
plt.cla()
