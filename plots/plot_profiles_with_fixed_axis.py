from netCDF4 import Dataset
import numpy as np
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import os

# in batch mode, without display
#matplotlib.use('Agg')  

file = 'OS_PIRATA-FR29_XBT.nc'
#ncpath = 'netcdf'
#path = 'plots'
ncpath = '.'
path = 'png'

ncfile = os.path.join(ncpath, file)
nc = Dataset(ncfile, mode='r')

TEMP = nc.variables['TEMP']
DEPTH = nc.variables['DEPTH']
PROFILE = nc.variables['PROFILE']
STATION = PROFILE.shape[0]
CM = nc.cycle_mesure

# move subplot outside loop prevent: RuntimeWarning: More than 20 figures have been opened.
fig, ax = plt.subplots()

for x in range(0,STATION):
    temp = TEMP[x,:]
    depth = DEPTH[x,:]
    #initialisation des variables pour determiner la profondeur max du tir
    A = 0
    B = 0
    PROF_DE_FIN = 0
    A = list(depth)
    B = A.index(max(A))

    if depth[B] > 1100:
        PROF_DE_FIN = 2500
        print('Station XBT a 2000m - T5')
    else:
        PROF_DE_FIN = 950
        print('Station XBT a 900m - T7')


    ax.plot(temp, depth)
    ax.invert_yaxis()
    ax.set(xlabel='{} ({})'.format(TEMP.long_name, TEMP.units), ylabel='{} ({})'.format(DEPTH.long_name,DEPTH.units),
           title='{} - XBT Sippican profile n° {}'.format(CM, x+1))
    ax.axis('auto')
    ax.set_ylim(top=0, bottom=PROF_DE_FIN)
    ax.set_xlim(left=0, right=32)
    ax.grid()

    figname = '{}-{:03d}_XBT.png'.format(CM, x+1)
    dest = os.path.join(path, figname)
    fig.savefig(dest)
    print('Printing: ', dest)
    #plt.show()
    plt.cla() 
#plt.close(fig)
print('Done.')