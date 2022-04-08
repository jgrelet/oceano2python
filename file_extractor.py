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
	    julian_day REAL NOT NULL UNIQUE,
	    latitude REAL NOT NULL,
	    longitude REAL NOT NULL,
        max_depth REAL,
        bottom_depth REAL
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

    def set_regex(self, cfg, ti):
        ''' prepare (compile) each regular expression inside toml file under section [<device>.header] 
        	[ctd.header]
	        isHeader = '^[*#]'
	        isDevice = '^\*\s+(Sea-Bird)'
	        TIME = 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)'
	        LATITUDE = 'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)'
	        LONGITUDE = 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)'
        '''

        # first pass on file(s)
        d = cfg[ti.lower()]['header']

        # fill the __regex dict with compiled regex 
        for key in d.keys():
            self.__regex[key] = re.compile(d[key])

    def read_files(self, cfg, device):

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

        for file in self.fname:
            with fileinput.input(
                file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f: 
                for line in f:
                    if self.__regex['isHeader'].match(line):
                        self.__header += line
                        continue
                    if self.__regex['endHeader'].match(line):
                        # read and decode header
                        #for k in self.__regex.keys():
                        # fake
                        print("insert station")
                        
                        self.db.insert("station", id = 1, header = self.__header,
                            date_time = "2022-04-06 12:00:00.000",
                            julian_day = 10.5, latitude = -10.2, longitude = 23.6)
                        continue

                    print(line)        
                    # split the line, remove leading and trailing space before
                    p = line.strip().split(self.__separator)
                    sql = 'station_id = 1'
                    # for key in self.keys:
                    #     # Insert data in profile table
                    #     sql += ", {} = {}".format(key, p[hash[key]])
                    # print(sql)
                    #sql = ', '.join(['{} = {}'.format(key, p[hash[key]]) for key in self.keys])
                    #print(sql)
                    sql = {}
                    #[sql[key] = p[hash[key]]  for key in self.keys]
                    sql['station_id'] = 1
                    for key in self.keys:
                        sql[key] = p[hash[key]] 
                    print(sql)
                    self.db.insert("profile",  sql )
                    #self.db.insert("profile", station_id = 1, PRES = 1, TEMP = 20, PSAL = 35, DOX2 = 20, DENS = 30)

        print('get sizes:')
        st = self.db.query('SELECT COUNT(id) FROM station')
        max_press = self.db.query('SELECT count(PRES) FROM profile')
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
    parser.add_argument('fname', nargs='*',
                        help='cnv file(s) to parse, (default: data/cnv/dfr29*.cnv)')

    # display extra logging info
    # see: https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    # https://docs.python.org/2/howto/argparse.html
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    fe = FileExtractor(args.fname, Roscop('code_roscop.csv'), args.keys)
    print("File(s): {}, Config: {}".format(args.fname, args.config))
    cfg = toml.load(args.config)
    fe.set_regex(cfg, args.instrument)
    fe.read_files(cfg, args.instrument)
    # print("Indices: {} x {}\nkeys: {}".format(fe.n, fe.m, fe.keys))
    # fe.second_pass(cfg, args.instrument, ['TIME', 'LATITUDE', 'LONGITUDE','BATH'])
    # # debug
    # print(fe['PRES'])
    # print(fe['TEMP'])
    # print(fe['PSAL'])
