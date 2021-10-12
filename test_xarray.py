# https://pumatest.nerc.ac.uk/cgi-bin/cf-checker.pl?cfversion=auto
import xarray as xr
import os
#import matplotlib.pyplot as plt

#plt.rcParams.update({'font.size': 20, 'figure.figsize': (10, 8)}) 

ncfiles = ['netcdf/OS_PIRATA-FR29_CTD.nc', 'netcdf/OS_PIRATA-FR29_XBT.nc','netcdf/OS_PIRATA-FR29_LADCP.nc']
for ncfile in ncfiles:
    ds = xr.open_dataset(ncfile)
    print(ds)
    df = ds.to_dataframe()
    print(df)