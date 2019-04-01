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
    if len(args)<6 or args[1]=='-h' or args[1]=='--help':
        print( main.func_doc.format(args[0]) )
        return 0



#===============================================================================
# input
#===============================================================================

    file_pressure = args[1]
    fichierpression = nc.Dataset(file_pressure)

    pbc_a=fichierpression.variables['Pbc_a'][:,:,:]
    pbc_G=fichierpression.variables['Pbc_G'][:,:,:]
    depth=fichierpression.variables['dept'][:]
    lon=fichierpression.variables['lont'][:]
    lat=fichierpression.variables['latt'][:]

    file_ssh = args[2]
    fichierssh = nc.Dataset(file_ssh)

    ssh_a=fichierssh.variables['ssh_a'][:,:]
    ssh_G=fichierssh.variables['ssh_G'][:,:]

    jj=pbc_a.shape[1]
    ii=pbc_a.shape[2]
    kk=pbc_a.shape[0]

    file_mean = args[3]
    fichierrhop = nc.Dataset(file_mean)
    rhop_m=fichierrhop.variables['rhop_mean'][0,:,:]

    file_mask = args[5]
    fichiermask = nc.Dataset(file_mask)
    gdepw=fichiermask.variables['gdepw'][0,:,:,:]
    gdept_0_all=fichiermask.variables['gdept_0'][0,74,:,:]
    gdept_0=fichiermask.variables['gdept_0'][0,0,:,:]
    tmask = fichiermask.variables['tmask'][0, :, :, :]




#===============================================================================
# output
#===============================================================================

    p_file=args[4]
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

    p_corr_a = ncfile.createVariable('P_corr_A',dtype('float32').char,('dept','y','x'))
    setattr(p_corr_a, 'standard_name',"Amplitude Of Pressure Total")
    setattr(p_corr_a, 'units',"m-1.kg.s-2")
    setattr(p_corr_a, 'coordinates', "dept latt lont")

    p_corr_G = ncfile.createVariable('P_corr_G',dtype('float32').char,('dept','y','x'))
    setattr(p_corr_G, 'standard_name',"Phase Of Pressure Total")
    setattr(p_corr_G, 'units',"m-1.kg.s-2")
    setattr(p_corr_G, 'coordinates', "dept latt lont")

#===============================================================================
# process
#===============================================================================

    print( 'Dimensions: kk={} jj={} ii={} '.format(kk,jj,ii) )

    p_zr = np.zeros(shape=(kk,jj,ii))
    p_zi = np.zeros(shape=(kk,jj,ii))

    ssh_zr = np.zeros(shape=(jj,ii))
    ssh_zi = np.zeros(shape=(jj,ii))

    grav=9.81


    for k in range (0,75):
        for j in range (0,484):
            for i in range (0,388):

                if math.isnan(pbc_a[k, j, i])==True:
                    p_zr[k, j, i] == np.NaN;
                    p_zi[k, j, i] == np.NaN;
                else:
                    p_zr[k, j, i]=pbc_a[k, j, i]*math.cos(math.radians(pbc_G[k, j, i]))
                    p_zi[k, j, i]=pbc_a[k, j, i]*math.sin(math.radians(pbc_G[k, j, i]))

    for j in range (0,484):
        for i in range (0,388):

            if math.isnan(ssh_a[j, i])==True:
                ssh_zr[j, i] == np.NaN;
                ssh_zi[j, i] == np.NaN;
            else:
                ssh_zr[j, i]=ssh_a[j, i]*math.cos(math.radians(ssh_G[j, i]))
                ssh_zi[j, i]=ssh_a[j, i]*math.sin(math.radians(ssh_G[j, i]))

    p_corr_zr = np.zeros(shape=(kk,jj,ii))
    p_corr_zi = np.zeros(shape=(kk,jj,ii))
    zz = np.zeros(shape=(jj,ii))

    for k in range (0,75):
        for j in range(0, 484):
            for i in range(0, 388):

                zz[j, i] = (0.5 * gdept_0[j,i]) + gdepw[k, j, i]
                p_corr_zr[k, j, i] = p_zr[k, j, i] + grav * rhop_m[j, i] * ssh_zr[j, i] * ((gdept_0_all[j,i] - zz[j,i]) / gdept_0_all[j,i])
                p_corr_zi[k, j, i] = p_zi[k, j, i] + grav * rhop_m[j, i] * ssh_zi[j, i] * ((gdept_0_all[j,i] - zz[j,i]) / gdept_0_all[j,i])


    p_a = np.zeros(shape=(kk,jj,ii))
    p_G = np.zeros(shape=(kk,jj,ii))


    for k in range (0,75):
        for j in range (0,484):
            for i in range (0,388):
                p_a[k, j, i] = (p_corr_zr[k, j, i] * p_corr_zr[k, j, i] + p_corr_zi[k, j, i] * p_corr_zi[k, j, i])**(0.5)
                p_G[k, j, i] = math.degrees(math.atan2(p_corr_zi[k, j, i], p_corr_zr[k, j, i]))

    p_a[tmask == 0] = nc.default_fillvals['f4']
    p_G[tmask == 0] = nc.default_fillvals['f4']
    p_corr_a[:,:,:] = p_a
    p_corr_G[:,:,:] = p_G




#===============================================================================
# clean-up
#===============================================================================

    fichierpression.close()
    fichierssh.close()
    fichierrhop.close()
    fichiermask.close()
    ncfile.close()


#*******************************************************************************
if __name__ == '__main__':
  #file:///usr/share/doc/packages/python/html/python-2.7-docs-html/library/sys.html#sys.exit
  sys.exit(main(sys.argv))

