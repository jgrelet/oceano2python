import logging
from netCDF4 import Dataset
from numpy import arange, dtype
from physicalParameter import Roscop


def writeNetCDF(fileName, fe):

    data = {}
    dims = ['TIME', 'LATITUDE', 'LONGITUDE', 'DEPTH']
    vars = dims.copy()

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
        vars.append(k)
    for key in vars:
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
        data[key] = nc.createVariable(
            key, dtype(hash['types']).char, dims, fill_value=fillvalue)
        # remove from the dictionary
        hash.pop('types')
        # create dynamically variable attributes
        for k in hash.keys():
            setattr(data[key], k, hash[k])

    # debug
    for key in vars:
        print(data[key])
