import logging
from netCDF4 import Dataset
from numpy import arange, complexfloating, dtype
import os
from datetime import datetime


def writeNetCDF(cfg, device, fe, r):

    # ncvars is a dictionary that store a netcdf variable for each physical parameter key
    ncvars = {}

    # variables and dimensions use for 1D and 2D variables
    #variables_1D = ['TIME', 'LATITUDE', 'LONGITUDE']
    #variables = variables_1D.copy()
    variables = fe.variables_1D
    dims_2D = ['time', 'level']

    # create the output directory if it does not exist
    if not os.path.exists(cfg['global']['netcdf']):
        os.makedirs(cfg['global']['netcdf'])

    # create netcdf file
    fileName = "{}/OS_{}_{}.nc".format(cfg['global']
                                       ['netcdf'], cfg['cruise']['cycleMesure'], device)
    if not os.path.exists(cfg['global']['ascii']):
        os.makedirs(cfg['global']['ascii'])
    nc = Dataset(fileName, "w", format="NETCDF3_CLASSIC")
    logging.debug(' ' + nc.data_model)
    print('writing netCDF file: {}'.format(fileName), end='')

    # create dimensions
    # n is number of profiles, m the max size of profiles
    time = nc.createDimension("time", fe.n)
    lat = nc.createDimension("latitude", fe.n)
    lon = nc.createDimension("longitude", fe.n)
    level = nc.createDimension('level', fe.m)

    # debug
    logging.debug(" level: {}, time: {}, lat: {}, lon: {}".format(
        len(level), len(time), len(lat), len(lon)))

    # create variables
    # add dimensions before variables list
    #for k in fe.keys:
    #    variables.append(k)
    # variables.extend(fe.keys())
    variables = fe.getlist()
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
        if any(key in item for item in fe.variables_1D):
            try:
                # create variable whit same dimension name, as TIME(time)
                ncvars[key] = nc.createVariable(
                    key, dtype(hash['types']).char, (key,), fill_value=fillvalue)
            except:
                # for BATH(time), it's a mess !
                ncvars[key] = nc.createVariable(
                    key, dtype(hash['types']).char, 'time', fill_value=fillvalue)
        else:
            ncvars[key] = nc.createVariable(
                key, dtype(hash['types']).char, dims_2D, fill_value=fillvalue)
        # remove from the dictionary
        hash.pop('types')
        # create dynamically variable attributes
        for k in hash.keys():
            setattr(ncvars[key], k, hash[k])
    nc._enddef()

    # add global attributes
    nc.data_type = "OceanSITES profile data"
    nc.Conventions = "CF-1.7"
    nc.title = cfg['global']['title']
    nc.institution = cfg['global']['institution']
    nc.source = cfg['global']['source']
    nc.comment = cfg['global']['comment']
    nc.references = cfg['global']['references']
    nc.cycle_mesure = cfg['cruise']['cycleMesure']
    nc.time_coverage_start = cfg['cruise']['beginDate']
    nc.time_coverage_end = cfg['cruise']['endDate']
    nc.timezone = cfg['cruise']['timezone']
    nc.data_assembly_center = cfg['cruise']['institute']
    nc.type_instrument = cfg[device.lower()]['typeInstrument']
    nc.instrument_number = cfg[device.lower()]['instrumentNumber']
    nc.date_update = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
    nc.pi_name = cfg['cruise']['pi']
    nc.processing_state = "1A"
    nc.codification = "OOPC"
    nc.format_version = "1.2"
    nc.Netcdf_version = "3.6"

    # debug
    for key in variables:
        logging.debug(" var: {}, dims: {}, shape: {}, dtype: {}, ndim: {}".format(
            key, ncvars[key].dimensions, ncvars[key].shape, ncvars[key].dtype, ncvars[key].ndim))

    # write the ncvars
    for key in variables:
        if any(key in item for item in fe.variables_1D):
            ncvars[key][:] = fe[key]
        else:
            ncvars[key][:, :] = fe[key]

    # close the netcdf file
    nc.close()
    print(' done...')
