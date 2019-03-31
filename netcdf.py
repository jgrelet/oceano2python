from netCDF4 import Dataset


def writeNetCDF(fileName, fe):

    # create netcdf file
    nc = Dataset(fileName, "w", format="NETCDF3_CLASSIC")
    print(nc.data_model)

    # create dimensions
    depth = nc.createDimension("DEPTH", None)
    time = nc.createDimension("TIME", None)
    lat = nc.createDimension("LATITUDE", 73)
    lon = nc.createDimension("LONGITUDE", 144)
