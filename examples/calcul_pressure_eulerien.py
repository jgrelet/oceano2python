#!/usr/bin/python

import sys
import numpy as np
import netCDF4 as nc
from numpy import arange, dtype

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

# ===============================================================================
# mask file
# ===============================================================================

    fichiermask=args[1]

    mask_file=nc.Dataset(fichiermask)
    depth=mask_file.variables['gdept_1d'][:]
    tmask=mask_file.variables['tmask'][0,:,:,:]
    e3t = mask_file.variables['e3t'][:,:,:,:]
    e3w = mask_file.variables['e3w'][:,:,:,:]
    mask_file.close()

#===============================================================================
# input
#===============================================================================

    fichierjulien=args[2]
    lefichier = nc.Dataset(fichierjulien)

    rhopv = lefichier.variables['rhop']
    ji=rhopv.shape[3]
    jj=rhopv.shape[2]
    jk=rhopv.shape[1]
    jl=rhopv.shape[0]

    ssh1 = lefichier.variables['ssh']



    itv=lefichier.variables['time_counter']

    lon=lefichier.variables['nav_lon_grid_T'][:]
    lat=lefichier.variables['nav_lat_grid_T'][:]

#===============================================================================
# output
#===============================================================================

    p_file=args[3]
    print('Creating '+p_file)

    # this will overwrite the file
    ncfile = nc.Dataset(p_file,'w', format='NETCDF3_CLASSIC')
    setattr(ncfile,'history',' '.join(args))
    ncfile.createDimension('x',ji)
    ncfile.createDimension('y',jj)
    ncfile.createDimension('dept',jk)
    ncfile.createDimension('time') # unlimited

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

    otv = ncfile.createVariable('time',dtype('float64').char,('time'))
    setattr(otv, 'units',itv.units)
    setattr(otv, 'standard_name',"time")
    setattr(otv, 'axis',"T")

    pv = ncfile.createVariable('Ptot',dtype('float32').char,('time','dept','y','x'))
    setattr(pv, 'standard_name',"Amplitude Of Pressure Total")
    setattr(pv, 'units',"m-1.kg.s-2")
    setattr(pv, 'coordinates', "time dept latt lont")

#===============================================================================
# process
#===============================================================================

    print( 'Dimensions: jl={} jk={} jj={} ji={}'.format(jl,jk,jj,ji) )

    p_tot=np.zeros(shape=(jk,jj,ji))

    grav=9.81

    for l in range(0,jl):

        time=itv[l]
        print( 'Time frame {}/{}'.format(l,jl) )

        e3t1=e3t[0, 0, :, :]
        e3w1=e3w[0, :, :, :]
        rhop=rhopv[l, :, :, :]
        ssh=ssh1[l, :, :]

        for k in range(0,jk):
            if k==0:
                p0=0.5*grav*e3t1*rhop[k,:,:]+(rhop[k,:,:]*grav*ssh[:,:])
            else:
                p0+=0.5*grav*e3w1[k,:,:]*(rhop[k,:,:]+rhop[k-1,:,:])

            p0*=tmask[k,:,:]
            p_tot[k,:,:]=p0

        p_tot[tmask==0]=nc.default_fillvals['f4']
        pv[l,:,:,:] = p_tot
        otv[l] = time

#===============================================================================
# clean-up
#===============================================================================

    lefichier.close()
    ncfile.close()


#*******************************************************************************
if __name__ == '__main__':
  #file:///usr/share/doc/packages/python/html/python-2.7-docs-html/library/sys.html#sys.exit
  sys.exit(main(sys.argv))
