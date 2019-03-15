'''
file_extractor.py
'''
import fileinput
import logging
import toml
import sys
import argparse
import numpy as np


class FileExtractor:

    '''
    This class read multiple ASCII file, extract physical parameter from ROSCOP codification at the given column
    and fill arrays
    '''

    # constructor with values by default
    def __init__(self, files):
        # attibutes
        # public:
        self.files = files
        self.n = 0
        self.m = 0
        # replace this constante with roscop fill value
        self.FillValue = 1e36

        # private:
        self.__headeer = {}
        self.__data = {}
    # overloading operators

    def __str__(self):
        ''' overload string representation '''
        return 'Class FileExtractor, file: %s, size = %d' % (self.files, len(self))

    def disp(self, keys):
        for key in keys:
            print("{}:".format(key))
            print(self.__data[key])

   # first pass on file(s)
    def firstPass(self):
        lineRead = 0
        filesRead = 0
        indMax = 0

        for file in self.files:
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
        return self.n, self.m

    # second pass, extract data from roscop code in files and fill array
    def secondPass(self, keys, dic):
        n = 0
        m = 0

        # initialize arrays, move at the end of firstPass ?
        for key in keys:
            # mult by __fillValue next
            # the shape parameter has to be an int or sequence of ints
            self.__data[key] = np.ones((self.n, self.m)) * self.FillValue

        for file in self.files:
            with fileinput.input(
                    file, openhook=fileinput.hook_encoded("ISO-8859-1")) as f:
                for line in f:
                    if line[0] == '#' or line[0] == '*':
                        continue
                    # split the line
                    p = line.split()

                    str = ' '
                    # fill array with extracted value of line for eack key (physical parameter)
                    for key in keys:
                        self.__data[key][n, m] = p[dic[key]]
                        # debug info
                        str += "{:>{width}}".format(
                            p[dic[key]], width=8)
                    logging.debug(str)

                    # increment m indice (the line number)
                    m += 1
            n += 1
            m = 0


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # python file_extractor.py data/cnv/dfr29*.cnv -d
    parser = argparse.ArgumentParser(
        description='This class read multiple ASCII file, extract physical parameter \
            from ROSCOP codification at the given column and fill arrays')
    parser.add_argument("-d", "--debug", help="display debug informations",
                        action="store_true")
    parser.add_argument("-k", "--key", nargs='+',
                        help="display dictionary for key(s), example -k TEMP [PSAL ...]")
    parser.add_argument(
        'files', nargs='*', help="cnv file(s) to parse, example data/cnv/dfr29*.cnv")

    # display extra logging info
    # see: https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    # https://docs.python.org/2/howto/argparse.html
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    fe = FileExtractor(args.files)
    cfg = toml.load('tests/test.toml')
    dic = cfg['split']['ctd']
    [n, m] = fe.firstPass()
    print("Indices:", n, m)
    fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], dic)
    fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])
