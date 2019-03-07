#!/usr/bin/python

import sys
import numpy as np
import netCDF4 as nc
from numpy import arange, dtype
import math

#*******************************************************************************
def main(args):

    """USE
  {0} mask.nc input.nc output.nc

DESCRIPTION
  Computes pressure from density and e3t (that changes with SSH).

"""
    if len(args)<4 or args[1]=='-h' or args[1]=='--help':
        print( main.func_doc.format(args[0]) )
        return 0



#===============================================================================
# input
#===============================================================================

    file_pressure_eulerien = args[1]
    fichierpression1 = nc.Dataset(file_pressure_eulerien)

    ptot_a=fichierpression1.variables['Ptot_a'][:,:,:]
    ptot_G=fichierpression1.variables['Ptot_G'][:,:,:]
    depth=fichierpression1.variables['dept'][:]
    lon=fichierpression1.variables['lont'][:]
    lat=fichierpression1.variables['latt'][:]

    jj=ptot_a.shape[1]
    ii=ptot_a.shape[2]
    kk=ptot_a.shape[0]


    file_pressure_lagpatch = args[2]
    fichierpression2 = nc.Dataset(file_pressure_lagpatch)
    P_corr_A=fichierpression2.variables['P_corr_A'][:,:,:]
    P_corr_G=fichierpression2.variables['P_corr_G'][:,:,:]



#===============================================================================
# output
#===============================================================================

    p_file=args[3]
    print('Creating '+p_file)

    # this will overwrite the file
    ncfile = nc.Dataset(p_file,'w', format='NETCDF3_CLASSIC')
    setattr(ncfile,'history',' '.join(args))
    ncfile.createDimension('x',ii)
    ncfile.createDimension('y',jj)
    ncfile.createDimension('dept',kk)


    data = ncfile.createVariable('lont',dtype('float64').char,('y','x'))
    data[:] = lon
    setattr(data, 'units',"degrees_north")
    setattr(data, 'standard_name',"longitude_at_T_location")

    data = ncfile.createVariable('latt',dtype('float64').char,('y','x'))
    data[:] = lat
    setattr(data, 'units',"degrees_east")
    setattr(data, 'standard_name',"latitude_at_T_location")

    data = ncfile.createVariable('dept',dtype('float64').char,('dept'))
    data[:] = depth
    setattr(data, 'units',"m")
    setattr(data, 'positive',"down")
    setattr(data, 'standard_name',"depth_at_T_location")
    setattr(data, 'axis',"Z")

    p_diff_a = ncfile.createVariable('P_corr_A',dtype('float32').char,('dept','y','x'))
    setattr(p_diff_a, 'standard_name',"Amplitude Of Pressure Total")
    setattr(p_diff_a, 'units',"m-1.kg.s-2")
    setattr(p_diff_a, 'coordinates', "dept latt lont")

    p_diff_G = ncfile.createVariable('P_corr_G',dtype('float32').char,('dept','y','x'))
    setattr(p_diff_G, 'standard_name',"Phase Of Pressure Total")
    setattr(p_diff_G, 'units',"m-1.kg.s-2")
    setattr(p_diff_G, 'coordinates', "dept latt lont")

#===============================================================================
# process
#===============================================================================

    p_diff_a[:,:,:] = ptot_a[:,:,:] - P_corr_A[:,:,:]
    p_diff_G[:,:,:] = ptot_G[:,:,:] - P_corr_G[:,:,:]


#===============================================================================
# clean-up
#===============================================================================

    fichierpression1.close()
    fichierpression2.close()
    ncfile.close()


#*******************************************************************************
if __name__ == '__main__':
  #file:///usr/share/doc/packages/python/html/python-2.7-docs-html/library/sys.html#sys.exit
  sys.exit(main(sys.argv))

