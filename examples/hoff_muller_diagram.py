import netCDF4 as nc

 from netCDF4 import Dataset

 import numpy as np

 import matplotlib.pyplot as plt

 import matplotlib.dates as dplt

 from pylab import *

 import os, sys

 mask = 
Dataset('/ccc/scratch/cont005/legos/nivertfl/VALIDATION_F01/INPUT_SAISON/HOFF-MULLER/total.nc', 
mode='r')
 trop = 
Dataset('/ccc/scratch/cont005/legos/nivertfl/VALIDATION_F01/INPUT_SAISON/HOFF-MULLER/sst_tropflux_1d_2000-regrid.nc', 
mode='r')
 mask1 = mask.variables['votemper'][:,0,:,:]
 trop1 = trop.variables['sst'][:,:,:]
 zbla=np.zeros(shape=(301,1))
 zblo=np.zeros(shape=(301,1))
 zbla2=np.zeros(shape=(301,366))
 zblo2=np.zeros(shape=(301,366))
 time = mask.variables['time_counter'][:]

 lon = mask.variables['nav_lon'][0,:]
 mask1[mask1 == 0] = np.NaN
 for y in range(0,365):
      for x in range(0,300):
          result1= np.nanmean(mask1[y,78:86,x])
          zbla[x,:]=result1
      zbla3=np.squeeze(zbla)
      zbla2[:,y]=zbla3
 zbla2=transpose(zbla2)

 for y in range(0,365):
     for x in range(0,300):
         result2= np.nanmean(trop1[y,78:86,x])
         zblo[x,:]=result2
     zblo3=np.squeeze(zblo)
     zblo2[:,y]=zblo3
 zblo2=transpose(zblo2)
 plt.clf()
 
 units=mask.variables['time_counter'].units
 
 from datetime import datetime
 buf=mask.variables['time_centered'][:];
 time=list()
 time.extend(buf.tolist())
 dates=nc.num2date(time,units,'gregorian').tolist()
 
 nt=len(dates)
 im1 = plt.figure(figsize=(6, 18))
 im1 = plt.contourf(lon,dates,zbla2, np.linspace(23,30,21), 
extend='both', cmap=cm.RdBu_r)
 plt.colorbar(im1,orientation='horizontal')
 im1 = plt.title("Modele annee 2000")
 plt.savefig('modele2000.png')
 plt.clf()
 im2 = plt.figure(figsize=(6, 18))
 im2 = plt.contourf(lon,dates,zblo2, np.linspace(23,30,21), 
extend='both', cmap=cm.RdBu_r)
 plt.colorbar(im2,orientation='horizontal')
 im2 = plt.title("TropFlux annee 2000")
 plt.savefig('obs2000.png')
