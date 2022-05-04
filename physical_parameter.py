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
        ''' overload r[key]
            for a given key return the values as a dictionary '''
        if key not in self.__hash:
            logging.error(
                " physicalParametr.py: invalid key: \"{}\"".format(key))
        else:
            return self.__hash[key]

    def __setitem__(self, key, value):
        ''' overload r[key] = value '''
        if type(value) is not dict:
            logging.error(
                " physicalParametr.py: the value: \"{}\" must be a dictionary".format(value))
            return

        if key not in self.__hash:
            self.__hash[key] = value
        else:
            logging.error(
                " physicalParametr.py: modify the existing key: \"{}\" is not allowed".format(key))

    def __repr__(self):
        ''' overload print() '''
        return super().__repr__()

    def __len__(self):
        ''' overload len() '''
        return len(self.__hash)

    # methods public
    def display_code(self, key):
        ''' for a given key print it's name and values as a dictionary '''
        print("%s :" % key)
        print(self[key])

    # read code roscop file
    def read(self):
        with open(self.file, 'rt') as f:

            # Create an object that maps the information in each row to an OrderedDict
            # the values in the first row of file f will be used as the fieldnames.
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                theKey = row[reader.fieldnames[0]]

                for k in reader.fieldnames:
                    # if the value of key is empty
                    if row[k] == '' or k == 'key':
                        # remove the key
                        row.pop(k)
                    else:
                        # use the second line with key string to convert each numeric type into float
                        if theKey != 'string':
                            if self['string'][k] == 'numeric':
                                if 'float' in row['types']:
                                   row[k] = float(row[k])
                                elif 'int' in row['types']:
                                   row[k] = int(row[k])
                                else:
                                    print('invalid type {}: {}'.format(theKey, k))
                        #logging.debug(
                        #    " {} -> {}, {} = {}".format(theKey, k, type(row[k]), row[k]))
                self.__hash[theKey] = row

        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":

    # usage:
    # > python physicalParameter.py code_roscop.csv -k TEMP -d
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
            print(f"{k}: {r[k]}")

    """ print("{}: {}".format(key[0], r[key[0]]['long_name']))
    r['TOTO'] = {'uncle': 'tata'}
    print(r['TOTO'])
    r['TEMP'] = 'tata' """
