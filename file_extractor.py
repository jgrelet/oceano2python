'''
file_extractor.py
'''
import fileinput
import logging
import toml
import sys
import argparse
import numpy as np
import re
from datetime import datetime
import tools

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
    def __init__(self, fname, roscop, keys, separator=None):
        # attibutes
        # public:
        self.fname = fname
        self.keys = keys
        self.roscop = roscop
        self.n = 0
        self.m = 0
        self.lineHeader = 0

        # private:
        self.__separator = separator
        self.__header = {}
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

    def first_pass(self):
        '''
        Returns
         ------
        out : [n,m]
        The size of array.
        '''
        lineHeader = 0
        lineData = 0
        filesRead = 0
        indMax = 0
        isHeader = True

        for file in self.fname:
            with fileinput.input(
                    file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f:
                lineData = 0
                lineHeader = 0
                isHeader = True
                filesRead += 1
                for line in f:
                    # header detection, skip header lines
                    if isHeader:
                        if 'isHeader' in self.__regex: 
                            if  self.__regex['isHeader'].match(line):
                                lineHeader += 1
                                continue
                        elif 'endHeader' in self.__regex:
                            if self.__regex['endHeader'].match(line):
                                lineHeader += 1
                                isHeader = False             
                            else:
                                lineHeader += 1
                                continue
    
                    # increment the line number
                    lineData += 1

                if lineData > indMax:
                    indMax = lineData
                logging.debug(
                    " {} -> header: {:>{w}} data: {:>{w2}}".format(
                        file, lineHeader, lineData, w=3, w2=6))
        # the size of arrays
        self.n = filesRead
        self.m = indMax
        self.lineHeader = lineHeader

    # second pass, extract data from roscop code in fname and fill array
    def second_pass(self, cfg, device, variables_1D):
        '''
        Read the file to its internal dict

        Parameters
        ----------
        keys: sequence, a list of physical parameter to read.
            ex: ['PRES', 'TEMP', 'PSAL']
        cfg: toml.load() instance, configuration file
        device: str, instrument
            ex: CTD,XBT or LADCP
        '''
        n = 0
        m = 0
        # initialize datetime object
        dt = datetime

        # set separator field if declared in toml section, none by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']

        # set skipHeader is declared in toml section, 0 by default

        # get the dictionary from toml block, device must be is in lower case
        hash = cfg['split'][device.lower()]

        # initialize arrays, move at the end of firstPass ?
        for key in variables_1D:
            #self.__data[key] = np.ones((self.n)) * self.__FillValue
            if '_FillValue' in self.roscop[key]:
                self.__data[key] = np.full(self.n, self.roscop[key]['_FillValue']) 
            else:
                self.__data[key] = np.empty(self.n) 
             
        for key in self.keys:
            # mult by __fillValue next
            # the shape parameter has to be an int or sequence of ints
            if '_FillValue' in self.roscop[key]:
                self.__data[key] = np.full([self.n, self.m], self.roscop[key]['_FillValue'])
            else:
                self.__data[key] = np.empty([self.n, self.m]) 

        for file in self.fname:
            with fileinput.input(
                file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f:
                day = month = year = hour = minute = second = 0
                for line in f:
                    if f.filelineno() < self.lineHeader + 1:
                        # read and decode header
                        for k in self.__regex.keys():
                            # key is DATETIME
                            if k == "DATETIME" and self.__regex[k].search(line):
                                (month, day, year, hour, minute, second) = \
                                    self.__regex[k].search(line).groups() 

                                # format date and time to  "May 09 2011 16:33:53"
                                dateTime = "%s/%s/%s %s:%s:%s"  %  (day, month, year, hour, minute, second)  
                                # set datetime object                              
                                dt = dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S")

                                # dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S")# dateTime conversion to "09/05/2011 16:33:53"
                                # dateTime = "%s" % \
                                #     (dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))  
                                # # conversion to "20110509163353"
                                # epic_date = "%s" % \
                                #     (dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S"))  

                                # # conversion to julian day
                                # julian = float((dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%j"))) \
                                # + ((float(hour) * 3600.) + (float(minute) * 60.) + float(second) ) / 86400.

                                # # we use julian day with origine 0
                                # julian -= 1
                                self.__data['TIME'][n] = tools.dt2julian(dt)  
                            # key is DATE
                            if k == "DATE" and self.__regex[k].search(line):
                                if device.lower() == 'ladcp':
                                    (year, month, day) = \
                                    self.__regex[k].search(line).groups() 
                                else:
                                    (month, day, year) = \
                                    self.__regex[k].search(line).groups() 
                            # key is TIME
                            if k == "TIME" and self.__regex[k].search(line):
                                (hour, minute, second) = \
                                self.__regex[k].search(line).groups()   
                       
                                # format date and time to  "May 09 2011 16:33:53"
                                dateTime = "%s/%s/%s %s:%s:%s"  %  (day, month, year, hour, minute, second)

                                # dateTime conversion to "09/05/2011 16:33:53"
                                dateTime = "%s" % \
                                    (dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))  
                                    
                                # set datetime object     
                                dt = dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S")
                                # # conversion to "20110509163353"
                                # epic_date = "%s" % \
                                #     (dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S"))  

                                # # conversion to julian day
                                # julian = float((dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%j"))) \
                                # + ((float(hour) * 3600.) + (float(minute) * 60.) + float(second) ) / 86400.

                                # # we use julian day with origine 0
                                # julian -= 1
                                self.__data['TIME'][n] = tools.dt2julian(dt)    
                            # key is LATITUDE
                            if k == "LATITUDE" and self.__regex[k].search(line):
                                if device.lower() == 'ladcp':
                                    [latitude] = self.__regex[k].search(line).groups()                                  
                                else:
                                    (lat_deg, lat_min, lat_hemi) = self.__regex[k].search(line).groups() 

                                    # format latitude to string
                                    latitude_str = "%s%c%s %s" % (lat_deg, tools.DEGREE, lat_min, lat_hemi)

                                    # transform to decimal using ternary operator
                                    latitude = float(lat_deg) + (float(lat_min) / 60.) if lat_hemi == 'N' else \
                                        (float(lat_deg) + (float(lat_min) / 60.)) * -1
                                self.__data['LATITUDE'][n] = latitude  
                            # key is LONGITUDE
                            if k == "LONGITUDE" and self.__regex[k].search(line):
                                if device.lower() == 'ladcp':
                                    [longitude] = self.__regex[k].search(line).groups()
                                else:
                                    (lon_deg, lon_min, lon_hemi) = self.__regex[k].search(line).groups() 

                                    # format longitude to string
                                    longitude_str = "%s%c%s %s" % (lon_deg, tools.DEGREE, lon_min, lon_hemi)

                                    # transform to decimal using ternary operator
                                    longitude = float(lon_deg) + (float(lon_min) / 60.) if lon_hemi == 'E' else \
                                        (float(lon_deg) + (float(lon_min) / 60.)) * -1
                                self.__data['LONGITUDE'][n] = longitude  
                            # key is BATH
                            if k == "BATH" and self.__regex[k].search(line):
                                [bath] = self.__regex[k].search(line).groups() 
                                self.__data['BATH'][n] = bath
                        continue

                    # split the line, remove leading and trailing space before
                    p = line.strip().split(self.__separator)

                    str = ' '
                    # fill array with extracted value of line for eack key (physical parameter)
                    for key in self.keys:
                        self.__data[key][n, m] = p[hash[key]]
                        # debug info
                        str += "{:>{width}}".format(
                            p[hash[key]], width=8)
                    logging.debug(str)

                    # increment m indice (the line number)
                    m += 1
            n += 1
            m = 0


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # > python file_extractor.py data/CTD/cnv/dfr2900[1-3].cnv -d
    # > python file_extractor.py data/CTD/cnv/dfr2900[1-3].cnv -k PRES TEMP PSAL DOX2 DENS
    # > python file_extractor.py data/CTD/cnv/dfr29*.cnv -d
    parser = argparse.ArgumentParser(
        description='This class read multiple ASCII file, extract physical parameter \
            from ROSCOP codification at the given column and fill arrays ',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
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

    fe = FileExtractor(args.fname, args.keys)
    print("File(s): {}, Config: {}".format(args.fname, args.config))
    cfg = toml.load(args.config)
    fe.first_pass()
    print("Indices: {} x {}\nkeys: {}".format(fe.n, fe.m, fe.keys))
    fe.second_pass(cfg, 'ctd')
    # debug
    # print(fe.disp())
