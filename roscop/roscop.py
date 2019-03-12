import csv
import shelve
import sys
import logging
import argparse


class Roscop:

    '''
    This class read a csv file describing physical parameter with ROSCOP codification
    '''

    # constructor with values by default
    def __init__(self, file):
        self.file = file
        self.hash = {}

    # call by print()
    def __str__(self):
        return 'Class Roscop, file: %s, size = %d' % (self.file, len(self.hash))

    def disp(self, theKey):
        print("%s :" % theKey)
        print(self.hash[theKey])

    # read code roscop file
    def read(self):
        with open(self.file, 'rt') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                theKey = row[reader.fieldnames[0]]
                for k in reader.fieldnames:
                    # if the value of key is empty
                    if row[k] == '':
                        # remove the key
                        row.pop(k)
                    else:
                        logging.debug("%s: %s" % (k, row[k]))
                self.hash[theKey] = row

        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # display extra logging info
    # see: https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    parser = argparse.ArgumentParser(
        description='This class Roscop parse a csv file describing physical parameter codification')
    parser.add_argument("-d", "--debug", help="display debug informations",
                        action="store_true")
    parser.add_argument("file", type=str, help="the csv file to parse")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Read the csv file and create an instance of Roscop class
    r = Roscop(args.file)
    #r = Roscop("code_roscop.csv")
    r.read()
    print(r)
    # r.disp('TEMP')
    r.disp('BATH')
