'''
file_extractor.py
'''
import fileinput
import linecache
import logging
from operator import length_hint
import string
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
import ascii
import odv
import netcdf

# define the data table
# the ID is actually the rowid AUTOINCREMENT column.
# removal of the UNIQUE constraint on DAYD, Casino bug ? DAYD REAL NOT NULL UNIQUE,
table_data = """
        CREATE TABLE data (
        ID INTEGER PRIMARY KEY,
        DAYD REAL NOT NULL,
        LATITUDE REAL NOT NULL,
        LONGITUDE REAL NOT NULL
        ); """

class Trajectory:

    '''
    This class read multiple ASCII file, extract physical parameter from ROSCOP codification at the given column
    and fill arrays.
    Header values and 1 dimensions variables as TIME, LATITUDE and LONGITUDE are 
    automaticaly extracted from toml configuration file, actually bi set_regexp function, may be add inside constructor ?

    Parameters
    ----------
    fname : files, str, pathlib.Path, list of str
        File, filename, or list to read and process.
    roscop: file which describe physical parameter (code_roscop.csv) 
    keys: list of physical parameter to extract
    dbname: sqlite3 file, default i in memory 
    separator : str, column separator, default None (blank)
    '''

    def __init__(self, fname, roscop, keys, dbname=":memory:", separator=None):
        '''constructor with values by default'''
        # private attibutes:
        self.__dbname = dbname
        self.__separator = separator
        self.__julianOrigin = 0
        self.__header = ''
        self.__data = {}
        self.__regex = {}
        self.__year = []

        # public attibutes:
        self.fname = fname
        self.keys = keys
        self.roscop = roscop
        self.encoding = "ISO-8859-1"
        self.n = 0
        self.m = 0
        self.lineHeader = 0
        self.db = SqliteDb(self.__dbname) 

    @property
    def year(self):
        return self.__year

    @property
    def julianOrigin(self):
        return self.__julianOrigin

    @property
    def julian_from_year(self):
        return tools.dt2julian(datetime(year=self.year, day=1, month=1))

    def iskey(self, key):
        ''' return true ik key is in dict self.__data '''
        if key in self.__data:
            return True
        else:
            return False

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
        return 'Class Trajectory, file: %s, size = %d x %d' % (self.fname, self.n, self.m)

    def update_table(self, keysList):
        ''' update table data and add new column from pm (physical parameter)'''
        # if LATITUDE and LONGITUDE are read as a variable, remove them from variables list
        keys = keysList.copy()
        if 'LATITUDE' in keys: keys.remove('LATITUDE')
        if 'LONGITUDE' in keys: keys.remove('LONGITUDE')
        for pm in keys:
            logging.debug(f"\tUpdate table data with new column {pm}")
            addColumn = f"ALTER TABLE data ADD COLUMN {pm} REAL NOT NULL"
            self.db.query(addColumn)

    def create_tables(self):
        ''' Create table data'''
        self.db.query("DROP TABLE IF EXISTS data")

        # Create table data
        self.db.query(table_data)

        # update table
        self.update_table(self.keys)

    def close(self):
        self.db.close()

    # get the keys list from __data
    def getlist(self):
        ''' return keys '''
        return self.__data.keys()

    def disp(self):
        # for key in keys:
        #     print("{}:".format(key))
        #     print(self.__data[key])
        buf = ''
        for key in self.keys:
            buf += "{}:\n".format(key)
            buf += "{}\n".format(self.__data[key])
        return buf

    def set_regex(self, cfg, ti, section):
        ''' prepare (compile) each regular expression inside toml file under section [<device>.header] 
        	[ctd.header]
	        isHeader = '^[*#]'
	        isDevice = '^\*\s+(Sea-Bird)'
	        TIME = 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)'
	        LATITUDE = 'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)'
	        LONGITUDE = 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)'
        '''

        # first pass on file(s)
        d = cfg[ti.lower()][section]

        # fill the __regex dict with compiled regex 
        for key in d.keys():
            self.__regex[key] = re.compile(d[key])

    

    def update_arrays(self):
        ''' extract data from sqlite database and fill self.__data arrays
        '''
        # print infos after reding all files   
        n = self.db.count('data')
        
        #m = self.db.max('data')
        # need more documentation about return dict from select
        #n = int(st[0]['COUNT(ID)']) 
        #m = int(max_size[0][f"MAX({self.keys[0]})"])
        print(f"Array sizes: {n}")

        # get data from table station and fill array
        query = self.db.select('data')

        # initialize one dimension variables
        for idx, item in enumerate(query):
            # define array size from table column name
            
            for k in item:  
                # k is a type of <class 'notanorm.base.CIKey'>, convert to char !!!
                key = f"{k}"
                if idx == 0:                  
                    if key != 'ID':          
                        #print(f"{key}:  {self.roscop[key]}")
                        if '_FillValue' in self.roscop[key]:
                                self.__data[key] = np.full(n, self.roscop[key]['_FillValue']) 
                        else:
                                self.__data[key] = np.empty(n)
                    else:
                        self.__data[key] = np.empty(n) 
                # fill arrays
                self.__data[key][idx] = item[key]
        
        self.n = n
        if n == 0:
            sys.exit("No file read ! Are you in the right directory ? Check for a match between the file names and the toml configuration file")    
        
        # save all database columns as key
        self.keys = self.__data.keys()

    def read_files(self, cfg, device):

        logging.debug("Enter in read_files()")
        # initialize datetime object
        dt = datetime

        # get the dictionary from toml block, device must be is in lower case
        hash = cfg[device.lower()]['split']

        # set separator field if declared in toml section, none by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']

        # set julian day origin field if declared in toml section, zero by default
        if 'julianOrigin' in cfg[device.lower()]:
            self.__julianOrigin = cfg[device.lower()]['julianOrigin']

        # read each file and extract header and data and fill sqlite tables
        for file in self.fname:
            process_header = False
            process_data = False

            # select the file encoding, default is "ISO-8859-1" for windows files, or "utf-8"
            if 'defaultEncoding' in  cfg['global']:
                self.encoding = cfg['global']['defaultEncoding']
            if 'encoding' in cfg[device.lower()]:
                self.encoding = cfg[device.lower()]['encoding']

            with fileinput.input(file, openhook=fileinput.hook_encoded(self.encoding)) as f: 
                sql = {}
                self.__header = ''
                print(f"Reading file: {file}")
                # read all lines in file 
                for line in f:
                    # if header line, save to __header private property and go to next line
                    #logging.debug(f"line read: {line}")
                    if 'endHeader' in self.__regex and self.__regex['endHeader'].match(line):
                        
                        for k in self.__regex.keys():
                        # key is DATETIME
                            if k == "DATETIME" and self.__regex[k].search(self.__header):
                                month, day, year, hour, minute, second = \
                                    self.__regex[k].search(self.__header).groups() 
                                if not self.__year:
                                    self.__year = int(year)
                        process_data = True
                        continue
                    if 'isHeader' in self.__regex and self.__regex['isHeader'].match(line):
                        self.__header += line 
                        continue
                    if 'isData' in self.__regex and self.__regex['isData'].search(line):
                        process_data = True

                    if process_data:
                        sql = {}
                        if 'TIME' in self.__regex and self.__regex['TIME'].search(line):
                            hour, minute, second = \
                            self.__regex['TIME'].search(line).groups() 
                            #print(f"{hour}:{minute}:{second}")
                        if 'DATE' in self.__regex and  self.__regex['DATE'].search(line):
                            day, month, year = \
                            self.__regex['DATE'].search(line).groups() 
                            #print(f"{day}/{month}/{year}")
                            # format date and time to  "May 09 2011 16:33:53"
                            dateTime = f"{day}/{month}/{year} {hour}:{minute}:{second}" 
                             # set datetime object   
                            if 'dateTimeFormat' in cfg[device.lower()]:
                                dtf = cfg[device.lower()]['dateTimeFormat']  
                            else:
                                dtf = "%d/%m/%Y %H:%M:%S"                    
                            date_time = dt.strptime(dateTime, dtf)
                            sql['DAYD'] = tools.dt2julian(date_time)   
                        #print(dateTime)
                        if 'LATITUDE' in self.__regex and self.__regex['LATITUDE'].search(line):
                            (lat_hemi, lat_deg, lat_min) = \
                            self.__regex['LATITUDE'].search(line).groups() 
                            #print(f"{lat_deg} {lat_min} {lat_hemi}")
                            # transform to decimal using ternary operator
                            latitude = float(lat_deg) + (float(lat_min) / 60.) if lat_hemi == 'N' else \
                                    (float(lat_deg) + (float(lat_min) / 60.)) * -1
                            sql['LATITUDE'] = latitude  
                            #sql['lat'] = tools.Dec2dmc(float(latitude),'N')
                        if 'LONGITUDE' in self.__regex and self.__regex['LONGITUDE'].search(line):
                            (lon_hemi, lon_deg, lon_min) = \
                            self.__regex['LONGITUDE'].search(line).groups() 
                            #print(f"{lon_deg} {lon_min} {lon_hemi}")
                            longitude = float(lon_deg) + (float(lon_min) / 60.) if lon_hemi == 'E' else \
                                    (float(lon_deg) + (float(lon_min) / 60.)) * -1
                            sql['LONGITUDE'] = longitude  
                            #sql['lon'] = tools.Dec2dmc(float(longitude),'E')

                        # now, extract and process all data   
                        # split the line, remove leading and trailing space before
                        p = line.strip().split(self.__separator)
                        logging.debug(f"line split: {p}")

                        # skip if list p is empty, case of empty line
                        if not p:
                            continue

                        # insert data from list p with indice hash[key]
                        for key in self.keys:
                            if key == 'ETDD':
                                sql['DAYD'] = float(p[hash[key]].replace(',','.')) + \
                                    tools.dt2julian(datetime(self.year, day=1, month=1)) - float(self.julianOrigin)
                                sql['ETDD'] = float(p[hash[key]].replace(',','.')) - float(self.julianOrigin)
                            elif key == 'DAYD':
                                sql['DAYD'] = float(p[hash[key]].replace(',','.')) - float(self.julianOrigin)
                            elif key == 'LATITUDE':
                                sql['LATITUDE'] = float(p[hash[key]].replace(',','.')) 
                            elif key == 'LONGITUDE':
                                sql['LONGITUDE'] = float(p[hash[key]].replace(',','.')) 
                            else:
                                logging.debug(f"{key}, {hash[key]}, {p[hash[key]]}")
                                sql[key] = float(p[hash[key]].replace(',','.')) 
                        self.db.insert("data",  sql )
                        process_data = False
                # end of readline in file

        self.update_arrays()
        
    def process(self, args, cfg, ti):
        '''
        Extract data from ASCII files and return Trajectory instance and array size of extracted data

        Parameters
        ----------
            args : ConfigParser
            cfg : dict
                toml instance describing the file structure to decode
            ti : str {'CNV', 'XBT','LADCP','TSG',}
                The typeInstrument key

        Returns
        -------
            fe: Profile
            n, m: array size
        '''

        print('processing...')
        # check if no file selected or cancel button pressed
        logging.debug("File(s): {}, config: {}, Keys: {}".format(
            args.files, args.config, args.keys))

        # if physical parameters are not given from cmd line, option -k, use the toml <device>.split values
        if args.keys == None:
            args.keys = cfg[ti.lower()]['split'].keys()

        # extract header and data from files
        # if args.database:
        #     fe = Profile(args.files, self.roscop, args.keys, dbname='test.db')
        # else:
        #     fe = Profile(args.files, r, args.keys)
        self.create_tables()

        # prepare (compile) each regular expression inside toml file under section [<device=ti>.header]
        self.set_regex(cfg, ti, 'header')
        if 'format' in cfg[ti.lower()]:
            self.set_regex(cfg, ti, 'format')

        self.read_files(cfg, ti)
        
        # write ASCII hdr and data files
        ascii.writeTrajectory(cfg, ti, self, self.roscop)

        if cfg['global']['odv']:
            odv.writeTrajectory(cfg, ti, self, self.roscop)

        # write the NetCDF file
        netcdf.writeTrajectory(cfg, ti, self, self.roscop)

# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # python file_extractor.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -d
    # python file_extractor.py data/CTD/cnv/dfr2900*.cnv -i CTD -k PRES ETDD TEMP PSAL DOX2 DENS
    # python file_extractor.py data/XBT/T7_0000*.EDF -k DEPTH TEMP SVEL -i XBT
    # python file_extractor.py data/CTD/btl/fr290*.btl -i BTL -k BOTL DEPTH ETDD TE01 PSA1 DO11

    # typeInstrument is a dictionary as key: files extension
    typeInstrument = {'CTD': ('cnv', 'CNV'), 'XBT': (
    'EDF', 'edf'), 'LADCP': ('lad', 'LAD'), 'TSG': ('colcor','COLCOR'),
    'BTL': ('btl', 'BTL')}
    #variables_1D = ['TIME', 'LATITUDE', 'LONGITUDE','BATH']
    ti = typeInstrument  # an alias     
      
    parser = argparse.ArgumentParser(
        description='This class read multiple ASCII file, extract physical parameter \
            from ROSCOP codification at the given column and fill arrays ',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='config.toml')
    parser.add_argument('-i', '--instrument', nargs='?', choices=ti.keys(),
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-k', '--keys', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
                        help='display dictionary for key(s), (default: %(default)s)')
    parser.add_argument('files', nargs='*',
                        help='ASCII file(s) to parse')
    parser.add_argument('--sbe35', nargs='*', 
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

    # call fe with  dbname='test.db' to create db file, dbname='test.db'
    #fe = Trajectory(files, Roscop('code_roscop.csv'), args.keys, dbname='test.db')
    fe = Trajectory(files, Roscop('code_roscop.csv'), args.keys)
    fe.create_tables()
    logging.debug(f"File(s): {files}, Config: {args.config}")
    cfg = toml.load(args.config)
    fe.set_regex(cfg, args.instrument, 'header')
    fe.read_files(cfg, args.instrument)
    logging.debug(f"Indices: {fe.n} x {fe.m}\nkeys: {fe.keys}")
    # if args.sbe35 and args.instrument == 'BTL':
    #     sbe35 = []
    #     for t in args.sbe35:  
    #         sbe35 += glob(t)  
    #     fe.fname = sbe35
    #     fe.set_regex(cfg, args.instrument, 'header')
    #     fe.read_files(cfg, args.instrument)
    # elif args.sbe35 and args.instrument != 'BTL': 
    #     print("option --sbe35 can only be used with the BTL instrument (-i BTL)")
    #     exit

    # # debug
    logging.debug(fe.getlist())
    for k in fe.keys:
        for i in range(fe.n):
            logging.debug(f"{fe[k][i][1]} : {fe[k][i][fe.m-1]}")
    fe.close()
