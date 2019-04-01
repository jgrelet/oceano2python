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


class FileExtractor:

    '''
    This class read multiple ASCII file, extract physical parameter from ROSCOP codification at the given column
    and fill arrays.

    Parameters
    ----------
    fname : file, str, pathlib.Path, list of str
        File, filename, or list to read.
    separator : str, default None
    skip_header : int, optional
        The number of lines to skip at the beginning of the file.
    '''

    # constructor with values by defaul
    def __init__(self, fname, keys, separator=None, skip_header=0):
        # attibutes
        # public:
        self.fname = fname
        self.keys = keys
        self.n = 0
        self.m = 0

        # private:
        self.__skip_header = skip_header
        self.__separator = separator
        self.__header = {}
        self.__data = {}
        # replace this constante with roscop fill value
        self.__FillValue = 1e36

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
        return 'Class FileExtractor, file: %s, size = %d' % (self.fname, len(self))

    def disp(self):
        # for key in keys:
        #     print("{}:".format(key))
        #     print(self.__data[key])
        buf = ''
        for key in self.keys:
            buf += "{}:\n".format(key)
            buf += "{}\n".format(self.__data[key])
        return buf

    def re_compile(self):

       # first pass on file(s)

    def first_pass(self):
        '''
        Returns
         ------
        out : [n,m]
        The size of array.
        '''
        lineRead = 0
        filesRead = 0
        indMax = 0

        for file in self.fname:
            with fileinput.input(
                    file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f:
                filesRead += 1
                for line in f:
                    if line[0] == '#' or line[0] == '*':
                        continue

                    # increment the line number
                    lineRead += 1

                if lineRead > indMax:
                    indMax = lineRead
                logging.debug(
                    " file: {} -> read: {:>{width}}".format(
                        file, lineRead, width=6))
            lineRead = 0
        # the size of arrays
        self.n = filesRead
        self.m = indMax
        # return self.n, self.m

    # second pass, extract data from roscop code in fname and fill array
    def second_pass(self, cfg, device):
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

        # set skipHeader is declared in toml section, 0 by default
        if 'separator' in cfg[device.lower()]:
            self.__separator = cfg[device.lower()]['separator']
        if 'skipHeader' in cfg[device.lower()]:
            self.__skip_header = cfg[device.lower()]['skipHeader']
        logging.debug(self.__skip_header)

        # get the dictionary from toml block, device must be is in lower case
        hash = cfg['split'][device.lower()]

        # initialize arrays, move at the end of firstPass ?
        for key in self.keys:
            # mult by __fillValue next
            # the shape parameter has to be an int or sequence of ints
            self.__data[key] = np.ones((self.n, self.m)) * self.__FillValue

        for file in self.fname:
            with fileinput.input(
                    file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f:
                for line in f:
                    if f.filelineno() < self.__skip_header + 1:
                        continue
                    if line[0] == '#' or line[0] == '*':
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
