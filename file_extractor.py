'''
file_extractor.py
'''
import fileinput
import linecache
import logging
from operator import length_hint
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
        station INT NOT NULL UNIQUE,
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

# define the data table
# the id is actually the rowid AUTOINCREMENT column.
table_data = """
        CREATE TABLE data (
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
    variables_1D = ['PROFILE', 'TIME', 'LATITUDE', 'LONGITUDE','BATH']

    # constructor with values by defaul
    def __init__(self, fname, roscop, keys, dbname=":memory:", separator=None):
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
        self.__year = []
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
        #max_size = self.db.query(f"SELECT COUNT({self.keys[0]}) FROM data")
        n = self.db.count('station')
        m = self.db.count('data')
        # need more documentation about return dict from select
        #n = int(st[0]['COUNT(id)']) 
        #m = int(max_size[0][f"COUNT({self.keys[0]})"])
        print(f"get sizes: {n} x {m}")

        for k in self.variables_1D:
            #print(self.roscop[k])
            if '_FillValue' in self.roscop[k]:
                    self.__data[k] = np.full(n, self.roscop[k]['_FillValue']) 
            else:
                    self.__data[k] = np.empty(n) 

        #query = self.db.query('SELECT julian_day, latitude, longitude, bath FROM station')
        query = self.db.select('station', ['id','station', 'julian_day', 'end_date_time',
            'latitude', 'longitude', 'bath'])
        #print(query)

        profil_pk = []
        for idx, item in enumerate(query):
            profil_pk.append(item['id'])
            self.__data['PROFILE'][idx] = item['station']
            #print(item['station'])
            self.__data['TIME'][idx] = item['julian_day']
            #self.__data['END_TIME'][idx] = item['end_date_time']
            self.__data['LATITUDE'][idx] = item['latitude']
            self.__data['LONGITUDE'][idx] = item['longitude']
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

    def read_files(self, cfg, device):

        # initialize datetime object
        dt = datetime

        # Create table station
        #db.query("DROP DATABASE IF EXISTS '{}'".format(fname))
        self.db.query(table_station)

        # Create table data
        self.db.query(table_data)

        # update table data and add new column from pm (physical parameter)
        for pm in self.keys:
            #print(f"\tUpdate table data with new column {pm}")
            addColumn = f"ALTER TABLE data ADD COLUMN {pm} REAL NOT NULL"
            self.db.query(addColumn)

        # get the dictionary from toml block, device must be is in lower case
        hash = cfg['split'][device.lower()]

        # set separator field if declared in toml section, none by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']

        # read each file and extract header and data and fill sqlite tables
        for file in self.fname:
            process_header = False
            process_data = False
            station = []
            with fileinput.input(
                file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f: 
                sql = {}
                self.__header = ''
                print(f"Reading file: {file}")
                # read all lines in file 
                for line in f:
                    # if header line, save to __header private property and go to next line
                    if 'endHeader' in self.__regex:
                        if self.__regex['endHeader'].match(line):
                            process_header = True
                    if 'isHeader' in self.__regex:
                        if self.__regex['isHeader'].match(line):
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

                        #print(f"Enter in process header : {self.__header}")
                        #print(f"Header with line: {line}")
                        
                        # read and decode header for each entries in configuration 
                        # toml file, section [device.header]
                        for k in self.__regex.keys():

                            # extract STATION number
                            if k == "station" and self.__regex[k].search(self.__header):
                                [station] = self.__regex[k].search(self.__header).groups() 
                                #print("station: {}, type: {}".format(station, type(station)))
                                sql['station'] = int(station)

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
                        sql['date_time'] = dt.strptime(dateTime, dtf)
                        sql['julian_day'] = tools.dt2julian(sql['date_time'])  
                                
                        #print(f"insert station: {sql}")
                        # insert or query return last cursor, get the value of the primary key
                        # with lastrowid
                        ret = self.db.insert("station", sql)  
                        pk = ret.lastrowid 
                        #print(f"Return: {pk}")                    
                        continue
                    # end of if process_header:

                    if process_data:

                        # now, extract and process all data   
                        # split the line, remove leading and trailing space before
                        p = line.strip().split(self.__separator)
                        #print(p)
                        sql = {}
                        #[sql[key] = p[hash[key]]  for key in self.keys]
                        sql['station_id'] = pk
                        for key in self.keys:
                            sql[key] = p[hash[key]] 
                        #self.db.insert("data", station_id = 1, PRES = 1, TEMP = 20, PSAL = 35, DOX2 = 20, DENS = 30)
                        self.db.insert("data",  sql )

                # end of readline in file

            # add end_date_time in station table if ETDD (julian) is present in data
            if 'ETDD' in self.keys:
                jj = tools.dt2julian(datetime(year=self.__year, day=1, month=1))
                dt = tools.julian2dt(float(sql['ETDD'])+jj-1)
                #print(dt.strftime("%d/%m/%Y %H:%M:%S"))
                self.db.update("station", id = pk, 
                    end_date_time = dt.strftime("%Y-%m-%d %H:%M:%S"))

                #self.db.update("station", id = pk, end_date_time = dt)

        self.update_arrays()
        


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # > python file_extractor.py data/CTD/cnv/dfr2900[1-3].cnv -d -i CTD
    # > python file_extractor.py data/CTD/cnv/dfr2900*.cnv -k PRES ETDD TEMP PSAL DOX2 DENS -i CTD
    # > python file_extractor.py data/XBT/T7_0000*.EDF -k DEPTH TEMP SVEL -i XBT
      
    parser = argparse.ArgumentParser(
        description='This class read multiple ASCII file, extract physical parameter \
            from ROSCOP codification at the given column and fill arrays ',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
    parser.add_argument('-i', '--instrument', nargs='?', choices=['CTD','XBT','LADCP'],
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
    #print(f"File(s): {files}, Config: {args.config}")
    cfg = toml.load(args.config)
    fe.set_regex(cfg, args.instrument, 'header')
    fe.read_files(cfg, args.instrument)
    # print(f"Indices: {fe.n} x {fe.m}\nkeys: {fe.keys}")
    # # debug
    #print(fe['PRES'])
    print(fe['TEMP'][0][1])
    print(fe.getlist())
    # print(fe['PSAL'])
