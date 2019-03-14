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
        # attibutes
        # public:
        self.file = file
        # private:
        self.__hash = {}
        # constructor build objet by reading the file
        self.read()

    # overloading operators
    def __str__(self):
        ''' overload string representation '''
        return 'Class Roscop, file: %s, size = %d' % (self.file, len(self))

    def __getitem__(self, key):
        ''' overload r[key] '''
        if key not in self.__hash:
            logging.error(
                " Invalid key: \"{}\"".format(key))
        else:
            return self.__hash[key]

    def __setitem__(self, key, value):
        ''' overload r[key] = value '''
        if type(value) is not dict:
            logging.error(
                " The value: \"{}\" must be a dictionary".format(value))
            return

        if key not in self.__hash:
            self.__hash[key] = value
        else:
            logging.error(
                " Modify the existing key: \"{}\" is not allowed".format(key))

    def __repr__(self):
        ''' overload print() '''
        return super().__repr__()

    def __len__(self):
        ''' overload len() '''
        return len(self.__hash)

    # methods public
    def displayCode(self, key):
        ''' for a given key print it's name and values as a dictionary '''
        print("%s :" % key)
        print(self[key])

    def returnCode(self, key):
        ''' for a given key return the values as a dictionary '''
        return(self[key])

    # read code roscop file
    def read(self):
        with open(self.file, 'rt') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                theKey = row[reader.fieldnames[0]]
                for k in reader.fieldnames:
                    # if the value of key is empty
                    if row[k] == '' or k == 'key':
                        # remove the key
                        row.pop(k)
                    else:
                        # logging.debug(" %s -> %s: %s" % (theKey, k, row[k]))
                        logging.debug(
                            " {} -> {}: {}".format(theKey, k, row[k]))
                self.__hash[theKey] = row

        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # > python physicalParameter.py code_roscop.csv -k TEMP
    parser = argparse.ArgumentParser(
        description='This class Roscop parse a csv file describing physical parameter codification')
    parser.add_argument("-d", "--debug", help="display debug informations",
                        action="store_true")
    parser.add_argument("-k", "--key", nargs='+',
                        help="display dictionary for key(s), example -k TEMP [PSAL ...]")
    parser.add_argument("file", type=str, help="the csv file to parse")

    # display extra logging info
    # see: https://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging
    # https://docs.python.org/2/howto/argparse.html
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # Read the csv file and create an instance of Roscop class
    r = Roscop(args.file)
    # r = Roscop("code_roscop.csv")

    # r.read()
    print(r)

    # get -k arg(s) list
    key = args.key
    # if args list is empty, key contain NoneType
    if key is not None:
        for k in key:
            r.displayCode(k)

    print("{}: {}".format(key[0], r.returnCode(key[0])['long_name']))
    r['TOTO'] = {'uncle': 'tata'}
    print(r['TOTO'])
    r['TEMP'] = 'tata'
