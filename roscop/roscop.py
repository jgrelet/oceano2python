"""
code roscop
"""

import csv
import shelve
import sys


class db:
    def __setattr__(self, name, value):
        self.__dict__[name] = value


# class roscop
# ------------


class Roscop:

  # constructor with values by default
    def __init__(self, file):
        self.file = file
        self.hash = {}

    # call by print()
    def __str__(self):
        # print("%s:" % row[key],  end='')
        # print()
        return 'Class Roscop, file: %s, size = %d' % (self.file, len(self.hash))

    def disp(self, theKey):
        #(a,b) = self.hash[theKey].items()
        print(self.hash.items())
        # for attr, value in d.__dict__.items():
        #print(attr, value)
        # print(d.__dict__)

    # read code roscop file
    def read(self):
        d = db()
        with open(self.file, 'rt') as f:
            reader = csv.DictReader(f, delimiter=';')
            #print("%s" % (reader.fieldnames))
            for key in reader.fieldnames:
                d.key = key

            for row in reader:
                theKey = row[reader.fieldnames[0]]
                for k in reader.fieldnames:
                    d.k = row[k]
                self.hash[theKey] = d
                #print("Key : %s" % theKey)

        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":
    from roscop import Roscop
    r = Roscop("code_roscop.csv")
    r.read()
    print(r)
    r.disp('TEMP')
    r.disp('PSAL')
