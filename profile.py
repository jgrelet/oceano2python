'''
file_extractor.py
'''
import fileinput
import linecache
import logging
from operator import length_hint, ne
from tkinter import N
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
import netcdf

# define SQL station table
table_station = """
        CREATE TABLE station (
	    id INTEGER PRIMARY KEY,
        header TEXT,
        STATION INT NOT NULL UNIQUE,
	    DATE_TIME TEXT NOT NULL UNIQUE,
        end_date_time TEXT,
	    DAYD REAL NOT NULL UNIQUE,
	    LATITUDE REAL NOT NULL,
        lat TEXT,
	    LONGITUDE REAL NOT NULL,
        lon TEXT,
        max_depth REAL,
        bath REAL,
        patm REAL,
        tair REAL,
        operator
        );"""

# define the data table
# the id is actually the rowid AUTOINCREMENT column.
table_data = """
        CREATE TABLE data (
        id INTEGER PRIMARY KEY,
        station_id INTEGER,
        FOREIGN KEY (station_id) 
            REFERENCES STATION (id) 
        ); """

class Profile:

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
    variables_1D = ['PROFILE', 'TIME', 'LATITUDE', 'LONGITUDE','BATH']

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
        return 'Class Profile, file: %s, size = %d x %d' % (self.fname, self.n, self.m)

    def update_table(self, keys):
        ''' update table data and add new column from pm (physical parameter)'''
        for pm in keys:
            logging.debug(f"\tUpdate table data with new column {pm}")
            addColumn = f"ALTER TABLE data ADD COLUMN {pm} REAL NOT NULL"
            self.db.query(addColumn)

    def create_tables(self):
        ''' Create table station and data'''
        self.db.query("DROP TABLE IF EXISTS station")
        self.db.query("DROP TABLE IF EXISTS data")
        self.db.query(table_station)

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

    def set_regex(self, cfg, ti, header):
        ''' prepare (compile) each regular expression inside toml file under section [<device>.header] 
        	[ctd.header]
	        isHeader = '^[*#]'
	        isDevice = '^\*\s+(Sea-Bird)'
	        TIME = 'System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)'
	        LATITUDE = 'NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+\.\d+)\s+(\w)'
	        LONGITUDE = 'NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)'
        '''

        # first pass on file(s)
        d = cfg[ti.lower()][header]

        # fill the __regex dict with compiled regex 
        for key in d.keys():
            self.__regex[key] = re.compile(d[key])

    def update_arrays(self):
        ''' extract data from sqlite database and fill self.__data arrays
        '''
        # print infos after reding all files   
        hdr = self.db.query('SELECT * FROM station')
        #st = self.db.query('SELECT COUNT(id) FROM station')
        #print(f"SELECT COUNT({self.keys[0]}) FROM data")
        n = self.db.count('station')
        m = 0
        for i in range(1,n+1):
            query = self.db.query(f"SELECT COUNT({self.keys[0]}) FROM data where station_id = {i}")
            #print(query)
            size = int(query[0][f"COUNT({self.keys[0]})"])
            if size > m:
                m = size
        
        #m = self.db.max('data')
        # need more documentation about return dict from select
        #n = int(st[0]['COUNT(id)']) 
        #m = int(max_size[0][f"MAX({self.keys[0]})"])
        print(f"Array sizes: {n} x {m}")

        # initialize one dimension variables
        for k in self.variables_1D:
            #print(self.roscop[k])
            if '_FillValue' in self.roscop[k]:
                    self.__data[k] = np.full(n, self.roscop[k]['_FillValue']) 
            else:
                    self.__data[k] = np.empty(n) 

        # get data from table station and fill array
        #query = self.db.query('SELECT DAYD, latitude, longitude, bath FROM station')
        query = self.db.select('station', ['id','STATION', 'DAYD', 'end_date_time',
            'LATITUDE', 'LONGITUDE', 'bath'])
        logging.debug(query)
        profil_pk = []
        for idx, item in enumerate(query):
            profil_pk.append(item['id'])
            self.__data['PROFILE'][idx] = item['STATION']
            #print(item['STATION'])
            self.__data['TIME'][idx] = item['DAYD']
            #self.__data['END_TIME'][idx] = item['end_date_time']
            self.__data['LATITUDE'][idx] = item['LATITUDE']
            self.__data['LONGITUDE'][idx] = item['LONGITUDE']
            self.__data['BATH'][idx] = item['bath']

        # initialize array
        for k in self.keys:
            if '_FillValue' in self.roscop[k]:
                self.__data[k] = np.full([n, m], self.roscop[k]['_FillValue'])
            else:
                self.__data[k] = np.empty([n, m]) 
        # for each parameters
        for k in self.keys:
            # for each entries in station table, n is a list with indice start at 0
            for i in profil_pk:
                query = self.db.select('data', [k], station_id = profil_pk[i-1])
                for idx, item in enumerate(query):
                    self.__data[k][i-1, idx] = item[k]

        self.m = m
        self.n = n
        if n == 0:
            sys.exit("No file read, check for a match between the file names and the toml configuration file")    

    def read_files(self, cfg, device):

        logging.debug("Enter in read_files()")
        # initialize datetime object
        dt = datetime
        station_regex = None
        fileName_dict = {}
        new_fileName_dict ={}

        # get the dictionary from toml split block, device must be is in lower case
        hash = cfg[device.lower()]['split']

        # set separator field if declared in toml section, none by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']

        # set julian day origin field if declared in toml section, zero by default
        if 'julianOrigin' in cfg[device.lower()]:
            self.__julianOrigin = cfg[device.lower()]['julianOrigin']

        # prepare the regex to extract station number from filename by defaut
        # if [device]['station'] defined
        if 'station' in cfg[device.lower()]:
            station_regex = re.compile(cfg[device.lower()]['station'])
            logging.debug(f"Station regex: {station_regex}")
            # Sometimes, when files start with different letters, the argv list is not well ordered 
            for file in self.fname:
                if station_regex.search(file):
                    [station] = station_regex.search(file).groups()
                    fileName_dict[int(station)] = file
                else:  # filename dosn't match regex
                    continue
            # use list comprehension to reoder the dictionnary fileName_dict
            for v in sorted(fileName_dict.keys()):
                new_fileName_dict[v]= fileName_dict[v]
            # [(fileName_dict[key]= value) for (key, value) in sorted(fileName_dict.items(), key=lambda x: x[1])]
        else:
            # we have to build a dictionary from the list of files
            for i in range(1, len(self.fname)):
                new_fileName_dict[i] = self.fname[i-1]

        # read each file from dict and extract header and data, fill sqlite tables and array
        for station, file in new_fileName_dict.items():
            process_header = False
            process_data = False
            sql = {}

            # by default, station or profile number is extract from the filename
            if station_regex != None and station_regex.search(file):
                [station] = station_regex.search(file).groups()
                sql['STATION'] = int(station)
                logging.debug(f"Station match: {sql['STATION']}")


            with fileinput.input(
                file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f: 
                self.__header = ''
                print(f"Reading file: {file}")
                # read all lines in file 
                for line in f:
                    # if header line, save to __header private property and go to next line
                    if 'endHeader' in self.__regex and self.__regex['endHeader'].match(line):
                        process_header = True
                    if 'isHeader' in self.__regex and self.__regex['isHeader'].match(line):
                        self.__header += line 
                        if process_header:
                            pass                       
                        else:
                            continue
                    if not process_data:
                        if not 'isHeader' in self.__regex and not process_header:
                            self.__header += line 
                            continue
                        

                    # at the end of header, extract information from regex, insert data
                    # to the table station and go to next line
                    if process_header:

                        #logging.debug(f"Enter in process header : {self.__header}")
                        logging.debug(f"Header with line: {line}")
                        
                        # read and decode header for each entries in configuration 
                        # toml file, section [device.header]
                        for k in self.__regex.keys():

                            # extract STATION number if [device][header][station] is defined
                            if k == "station" and self.__regex[k].search(self.__header):
                                [station] = self.__regex[k].search(self.__header).groups() 
                                #print("station: {}, type: {}".format(station, type(station)))
                                sql['STATION'] = int(station)

                            # key is DATETIME
                            if k == "DATETIME" and self.__regex[k].search(self.__header):
                                month, day, year, hour, minute, second = \
                                    self.__regex[k].search(self.__header).groups() 
                                if not self.__year:
                                    self.__year = int(year)

                            # key is DATE
                            if k == "DATE" and self.__regex[k].search(self.__header):
                                if device.lower() == 'ladcp':
                                    year, month, day = \
                                    self.__regex[k].search(self.__header).groups() 
                                else:
                                    month, day, year = \
                                    self.__regex[k].search(self.__header).groups() 
                                #print(f"{day}/{month}/{year}")
                                if not self.__year:
                                    self.__year = int(year)

                            # key is TIME
                            if k == "TIME" and self.__regex[k].search(self.__header):
                                hour, minute, second = \
                                self.__regex[k].search(self.__header).groups()  

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
                                sql['lat'] = tools.Dec2dmc(float(latitude),'N')

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
                                sql['lon'] = tools.Dec2dmc(float(longitude),'E')

                            # key is BATH
                            if k == "BATH" and self.__regex[k].search(self.__header):
                                [bath] = self.__regex[k].search(self.__header).groups() 
                                sql['bath'] = bath

                        # end of matching regex inside header
                        process_header = False
                        process_data = True

                        # format date and time to  "May 09 2011 16:33:53"
                        dateTime = f"{day}/{month}/{year} {hour}:{minute}:{second}"  
                        # set datetime object   
                        if 'dateTimeFormat' in cfg[device.lower()]:
                            dtf = cfg[device.lower()]['dateTimeFormat']  
                        else:
                            dtf = "%d/%m/%Y %H:%M:%S"                    
                        sql['DATE_TIME'] = dt.strptime(dateTime, dtf)
                        sql['DAYD'] = tools.dt2julian(sql['DATE_TIME'])  
                                
                        # insert or query return last cursor, get the value of the primary key
                        # with lastrowid
                        ret = self.db.insert("station", sql)  
                        pk = ret.lastrowid          
                        continue
                    # end of if process_header:

                    if process_data:

                        # now, extract and process all data   
                        # split the line, remove leading and trailing space before
                        p = line.strip().split(self.__separator)
                        logging.debug(f"line split: {p}")
                        #logging.debug(f"line end: {p[-1]}")
                        
                        # skip to next line in file when skipLineWith is defined
                        if 'skipLineWith' in cfg[device.lower()]:             
                            #logging.debug(cfg[device.lower()]['skipLineWith'])
                            if cfg[device.lower()]['skipLineWith'] in p[-1]:
                                continue

                        sql = {}
                        # insert data from list p with indice hash[key]
                        #[sql[key] = p[hash[key]]  for key in self.keys]
                        sql['station_id'] = pk
                        for key in self.keys:
                            if key == 'ETDD' and  'julianOrigin' in cfg[device.lower()]:
                                sql[key] = float(p[hash[key]]) - float(self.julianOrigin)
                            else:
                                logging.debug(f"{key}, {hash[key]}, {p[hash[key]]}")
                                sql[key] = float(p[hash[key]]) 
                        #self.db.insert("data", station_id = 1, PRES = 1, TEMP = 20, PSAL = 35, DOX2 = 20, DENS = 30)
                        self.db.insert("data",  sql )

                # end of readline in file

            # add end_date_time in station table if ETDD (julian) is present in data
            if 'ETDD' in self.keys:
                # Seabird use julian day start at 1, we use jd start at 0
                tmp = tools.julian2format(float(sql['ETDD']) + self.julian_from_year)
                self.db.update("station", id = pk, end_date_time = tmp)

                #self.db.update("station", id = pk, end_date_time = dt)

        self.update_arrays()
        
    def process(self, args, cfg, ti):
        '''
        Extract data from ASCII files and return Profile instannce and array size of extracted data

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

        self.read_files(cfg, ti)
        #return fe
        # write ASCII hdr and data files
        ascii.writeProfile(cfg, ti, self, self.roscop)

        # write the NetCDF file
        netcdf.writeProfile(cfg, ti, self, self.roscop)

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
    #fe = Profile(files, Roscop('code_roscop.csv'), args.keys, dbname='test.db')
    fe = Profile(files, Roscop('code_roscop.csv'), args.keys)
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
