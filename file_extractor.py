'''
file_extractor.py
'''
import fileinput
import linecache
import logging
import toml
import sys
import argparse
import numpy as np
import re
from glob import glob
from datetime import datetime
import tools
from physical_parameter import Roscop
from notanorm import SqliteDb 

# define SQL station table
table_station = """
        CREATE TABLE station (
	    id INTEGER PRIMARY KEY,
        header TEXT,
	    date_time TEXT NOT NULL UNIQUE,
        end_date_time TEXT,
	    julian_day REAL NOT NULL UNIQUE,
	    latitude REAL NOT NULL,
        lat TEXT,
	    longitude REAL NOT NULL,
        lon TEXT,
        max_depth REAL,
        bath REAL,
        patm REAL,
        tair REAL,
        operator
        );"""

# define the profile table
# the id is actually the rowid AUTOINCREMENT column.
table_profile = """
        CREATE TABLE profile (
        id INTEGER PRIMARY KEY,
        station_id INTEGER,
        FOREIGN KEY (station_id) 
            REFERENCES station (id) 
        ); """

class FileExtractor:

    '''
    This class read multiple ASCII file, extract physical parameter from ROSCOP codification at the given column
    and fill arrays.
    Header values and 1 dimensions variables as TIME, LATITUDE and LONGITUDE are 
    automaticaly extracted from toml configuration file, actually bi set_regexp function, may be add inside constructor ?

    Parameters
    ----------
    fname : file, str, pathlib.Path, list of str
        File, filename, or list to read.
    keys: list of physical parameter to extract
    separator : str, column separator, default None (blank)
    '''

    # constructor with values by defaul
    def __init__(self, fname, roscop, keys, separator=None, dbname=":memory:"):
        # attibutes
        # public:
        self.fname = fname
        self.keys = keys
        self.roscop = roscop
        self.n = 0
        self.m = 0
        self.lineHeader = 0
        self.db = SqliteDb(dbname) 

        # private:
        self.__separator = separator
        self.__header = ''
        self.__data = {}
        self.__regex = {}
        # replace this constante with roscop fill value
        #self.__FillValue = 1e36

    # overloading operators
    def __getitem__(self, key):
        ''' overload r[key] '''
        if key not in self.__data:
            logging.error(
                " file_extractor.py: invalid key: \"{}\"".format(key))
        else:
            return self.__data[key]

    def __str__(self):
        ''' overload string representation '''
        return 'Class FileExtractor, file: %s, size = %d x %d' % (self.fname, self.n, self.m)

    def disp(self):
        # for key in keys:
        #     print("{}:".format(key))
        #     print(self.__data[key])
        buf = ''
        for key in self.keys:
            buf += "{}:\n".format(key)
            buf += "{}\n".format(self.__data[key])
        return buf

    def set_regex(self, cfg, ti, table):
        ''' prepare (compile) each regular expression inside toml file under section [<device>.header] 
        	[ctd.header]
	        isHeader = '^[*#]'
	        isDevice = '^\*\s+(Sea-Bird)'
	        TIME = 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)'
	        LATITUDE = 'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)'
	        LONGITUDE = 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)'
        '''

        # first pass on file(s)
        d = cfg[ti.lower()][table]

        # fill the __regex dict with compiled regex 
        for key in d.keys():
            self.__regex[key] = re.compile(d[key])

    def read_files(self, cfg, device):

        # initialize datetime object
        dt = datetime

        print('Create table station')
        #db.query("DROP DATABASE IF EXISTS '{}'".format(fname))
        self.db.query(table_station)

        print('Create table profile')
        self.db.query(table_profile)

        for pm in self.keys:
            print('\tUpdate table profile with new column {}'.format(pm))
            addColumn = "ALTER TABLE profile ADD COLUMN {} REAL NOT NULL".format(pm)
            self.db.query(addColumn)

        # get the dictionary from toml block, device must be is in lower case
        hash = cfg['split'][device.lower()]

        # set separator field if declared in toml section, none by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']

        # read each file and extract header and data and fill sqlite tables
        for file in self.fname:
            with fileinput.input(
                file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f: 
                sql = {}
                self.__header = ''
                print("Reading file: {}".format(file))
                # read all lines in file 
                for line in f:
                    # 
                    if self.__regex['isHeader'].match(line):
                        self.__header += line
                        continue
                    # at the end of header, extract information from regex, insert data
                    # to the table station and go to next line
                    if self.__regex['endHeader'].match(line):
                        
                        # read and decode header
                        for k in self.__regex.keys():

                            # extract STATION number
                            if k == "station" and self.__regex[k].search(self.__header):
                                [station] = self.__regex[k].search(self.__header).groups() 
                                sql['id'] = station
                                #print('station {}'.format(station))

                            # key is DATETIME
                            if k == "DATETIME" and self.__regex[k].search(self.__header):
                                (month, day, year, hour, minute, second) = \
                                    self.__regex[k].search(self.__header).groups() 

                                # format date and time to  "May 09 2011 16:33:53"
                                dateTime = "%s/%s/%s %s:%s:%s"  %  (day, month, year, hour, minute, second)  
                                # set datetime object                              
                                sql['date_time'] = dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S")
                                sql['julian_day'] = tools.dt2julian(sql['date_time'])  

                            # key is LATITUDE
                            if k == "LATITUDE" and self.__regex[k].search(self.__header):
                                if device.lower() == 'ladcp':
                                    [latitude] = self.__regex[k].search(self.__header).groups()                                  
                                else:
                                    (lat_deg, lat_min, lat_hemi) = self.__regex[k].search(self.__header).groups() 

                                    # format latitude to string
                                    latitude_str = "%s%c%s %s" % (lat_deg, tools.DEGREE, lat_min, lat_hemi)

                                    # transform to decimal using ternary operator
                                    latitude = float(lat_deg) + (float(lat_min) / 60.) if lat_hemi == 'N' else \
                                        (float(lat_deg) + (float(lat_min) / 60.)) * -1
                                sql['LATITUDE'] = latitude  
                                sql['lat'] = tools.Dec2dmc(latitude,'N')

                            # key is LONGITUDE
                            if k == "LONGITUDE" and self.__regex[k].search(self.__header):
                                if device.lower() == 'ladcp':
                                    [longitude] = self.__regex[k].search(self.__header).groups()
                                else:
                                    (lon_deg, lon_min, lon_hemi) = self.__regex[k].search(self.__header).groups() 

                                    # format longitude to string
                                    longitude_str = "%s%c%s %s" % (lon_deg, tools.DEGREE, lon_min, lon_hemi)

                                    # transform to decimal using ternary operator
                                    longitude = float(lon_deg) + (float(lon_min) / 60.) if lon_hemi == 'E' else \
                                        (float(lon_deg) + (float(lon_min) / 60.)) * -1
                                sql['LONGITUDE'] = longitude  
                                sql['lon'] = tools.Dec2dmc(longitude,'E')

                            # key is BATH
                            if k == "BATH" and self.__regex[k].search(self.__header):
                                [bath] = self.__regex[k].search(self.__header).groups() 
                                sql['bath'] = bath
                                
                        # print debug header values
                        # print('header from sql dict:')
                        # for k in sql.keys():
                        #     print(sql[k])

                        #print("insert station")
                        self.db.insert("station", sql)
                        continue

                    # now, extract and process all data
                    #print(line)        
                    # split the line, remove leading and trailing space before
                    p = line.strip().split(self.__separator)
                    # for key in self.keys:
                    #     # Insert data in profile table
                    #     sql += ", {} = {}".format(key, p[hash[key]])
                    # print(sql)
                    #sql = ', '.join(['{} = {}'.format(key, p[hash[key]]) for key in self.keys])
                    #print(sql)
                    sql = {}
                    #[sql[key] = p[hash[key]]  for key in self.keys]
                    sql['station_id'] = station
                    for key in self.keys:
                        sql[key] = p[hash[key]] 
                    #print(sql)
                    self.db.insert("profile",  sql )
                    #self.db.insert("profile", station_id = 1, PRES = 1, TEMP = 20, PSAL = 35, DOX2 = 20, DENS = 30)

            #print(sql['ETDD'])
            jj = tools.dt2julian(datetime(year=2019, day=1, month=1))
            dt = tools.julian2dt(float(sql['ETDD'])+jj-1)
            #print(dt.strftime("%d/%m/%Y %H:%M:%S"))
            self.db.update("station", id = station, 
                end_date_time = dt.strftime("%Y-%m-%d %H:%M:%S"))

        # print infos after reding all files
        print('get sizes:')
        hdr = self.db.query('SELECT * FROM station')
        st = self.db.query('SELECT COUNT(id) FROM station')
        max_press = self.db.query('SELECT max(PRES) FROM profile')
        # hdr is a list of dict
        # hdr[0] ={'id': 1, 'header': None, 'date_time': '2019-03-02 15:20:03', 
        # 'julian_day': 25262.638923611026, 'latitude': 12.492833333333333, 
        # 'longitude': -23.342666666666666, 'max_depth': None, 'bath': 4894.0}
        #print(hdr[0]['id'])
        for i in hdr:
            print(i['id'], i['date_time'], i['end_date_time'], i['lat'], i['lon'])
        print(st, max_press)


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage Unix:
    # > python file_extractor.py data/CTD/cnv/dfr2900[1-3].cnv -d -i CTD
    # > python file_extractor.py data/CTD/cnv/dfr2900*.cnv -k PRES TEMP PSAL DOX2 DENS -i CTD
    # 
    # usage DOS:
    # > python file_extractor.py data/CTD/cnv/dfr2900?.cnv -d -i CTD
    # > python file_extractor.py data/CTD/cnv/dfr2900?.cnv -k PRES TEMP PSAL DOX2 DENS -i CTD
    #
    parser = argparse.ArgumentParser(
        description='This class read multiple ASCII file, extract physical parameter \
            from ROSCOP codification at the given column and fill arrays ',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
    parser.add_argument('-i', '--instrument', nargs='?', choices=['CTD','XBT'],
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-k', '--keys', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
                        help='display dictionary for key(s), (default: %(default)s)')
    parser.add_argument('files', nargs='*',
                        help='ASCII file(s) to parse')

    # display extra logging info
    # see: https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    # https://docs.python.org/2/howto/argparse.html
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # work with DOs, Git bash and Linux
    files = []
    for file in args.files:  
        files += glob(file)  

    fe = FileExtractor(files, Roscop('code_roscop.csv'), args.keys)
    print("File(s): {}, Config: {}".format(files, args.config))
    cfg = toml.load(args.config)
    fe.set_regex(cfg, args.instrument, 'header')
    fe.read_files(cfg, args.instrument)
    # print("Indices: {} x {}\nkeys: {}".format(fe.n, fe.m, fe.keys))
    # fe.second_pass(cfg, args.instrument, ['TIME', 'LATITUDE', 'LONGITUDE','BATH'])
    # # debug
    # print(fe['PRES'])
    # print(fe['TEMP'])
    # print(fe['PSAL'])
