import logging
from netCDF4 import Dataset
from numpy import arange, dtype
from physicalParameter import Roscop


def writeNetCDF(fileName, fe):

    data = {}
    dims = ['TIME', 'LATITUDE', 'LONGITUDE']
    variables = dims.copy()
    dims_4d = dims.copy()
    dims_4d = dims_4d.append('DEPTH')

    # move to main after tests
    r = Roscop("code_roscop.csv")

    # create netcdf file
    nc = Dataset(fileName, "w", format="NETCDF3_CLASSIC")
    logging.debug(' ' + nc.data_model)

    # create dimensions
    # n is number of profiles, m the max size of profiles
    time = nc.createDimension("TIME", fe.n)
    lat = nc.createDimension("LATITUDE", fe.n)
    lon = nc.createDimension("LONGITUDE", fe.n)
    depth = nc.createDimension('DEPTH', fe.m)

    logging.debug(" depth: {}, time: {}, lat: {}, lon: {}".format(
        len(depth), len(time), len(lat), len(lon)))

    # create variables
    # add dimensions before variables list
    for k in fe.keys:
        variables.append(k)
    # variables.extend(fe.keys())
    print(variables)
    for key in variables:
        # for each variables get the attributes list
        hash = r.returnCode(key)
        # _FillValue attribute must be set when variable is created
        # (using fill_value keyword to createVariable)
        if '_FillValue' in hash:
            fillvalue = hash['_FillValue']
            # remove from the dictionary
            hash.pop('_FillValue')
        else:
            fillvalue = None
        # create the variable
        print(key)
        if any(key in item for item in dims):
            data[key] = nc.createVariable(
                key, dtype(hash['types']).char, (key,), fill_value=fillvalue)
        else:
            data[key] = nc.createVariable(
                key, dtype(hash['types']).char, dims_4d, fill_value=fillvalue)
        # remove from the dictionary
        hash.pop('types')
        # create dynamically variable attributes
        for k in hash.keys():
            setattr(data[key], k, hash[k])

    # debug
    for key in variables:
        print(data[key])
