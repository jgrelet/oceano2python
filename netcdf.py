import logging
from netCDF4 import Dataset
from numpy import arange, dtype
from physicalParameter import Roscop


def writeNetCDF(fileName, fe):

    data = {}
    variables_1D = ['TIME', 'LATITUDE', 'LONGITUDE']
    variables = variables_1D.copy()
    dims_2D = ['TIME', 'DEPTH']

    # move to main after tests
    r = Roscop("code_roscop.csv")

    # create netcdf file
    nc = Dataset(fileName, "w", format="NETCDF3_CLASSIC")
    logging.debug(' ' + nc.data_model)
    print('writing netCDF file: {}'.format(fileName))
    # create dimensions
    # n is number of profiles, m the max size of profiles
    time = nc.createDimension("TIME", fe.n)
    lat = nc.createDimension("LATITUDE", fe.n)
    lon = nc.createDimension("LONGITUDE", fe.n)
    depth = nc.createDimension('DEPTH', fe.m)

    # debug
    logging.debug(" depth: {}, time: {}, lat: {}, lon: {}".format(
        len(depth), len(time), len(lat), len(lon)))

    # create variables
    # add dimensions before variables list
    for k in fe.keys:
        variables.append(k)
    # variables.extend(fe.keys())
    for key in variables:
        # for each variables get the attributes dictionary from Roscop
        hash = r[key]
        # _FillValue attribute must be set when variable is created
        # (using fill_value keyword to createVariable)
        if '_FillValue' in hash:
            fillvalue = hash['_FillValue']
            # remove from the dictionary
            hash.pop('_FillValue')
        else:
            fillvalue = None
        # create the variable
        if any(key in item for item in variables_1D):
            data[key] = nc.createVariable(
                key, dtype(hash['types']).char, (key,), fill_value=fillvalue)
        else:
            data[key] = nc.createVariable(
                key, dtype(hash['types']).char, dims_2D, fill_value=fillvalue)
        # remove from the dictionary
        hash.pop('types')
        # create dynamically variable attributes
        for k in hash.keys():
            setattr(data[key], k, hash[k])
    nc._enddef()

    # debug
    for key in variables:
        logging.debug(" var: {}, dims: {}, shape: {}, dtype: {}, ndim: {}".format(
            key, data[key].dimensions, data[key].shape, data[key].dtype, data[key].ndim))

    # write the data
    for key in variables:
        if any(key in item for item in variables_1D):
            data[key][:] = fe[key]
        else:
            data[key][:, :] = fe[key]

    # close the netcdf file
    nc.close()
    print('done...')
