#!/usr/bin/env python
# 
# https://pumatest.nerc.ac.uk/cgi-bin/cf-checker.pl?cfversion=auto
import xarray as xr
import os
#import matplotlib.pyplot as plt

#plt.rcParams.update({'font.size': 20, 'figure.figsize': (10, 8)}) 

#ncfiles = ['netcdf/OS_PIRATA-FR29_CTD.nc', 'netcdf/OS_PIRATA-FR29_XBT.nc','netcdf/OS_PIRATA-FR29_LADCP.nc']
ncfiles = ['netcdf/OS_PIRATA-FR29_CTD.nc']
for file in ncfiles:
    print(f"Read {file}")
    # with automatically closes the dataset after use
    with xr.open_dataset(file) as ds:
        #print(type(ds.keys()))
        for key in ds.keys():
            print(f"{key} ", end='')
            #print(ds[k])
    #print(ds)
    #print(ds['PROFILE'])
    #df = ds.to_dataframe()
    #print(df)