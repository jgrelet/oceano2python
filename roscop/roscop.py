"""
code roscop
"""

import csv
import shelve
import sys


# class roscop
# ------------


class Roscop:

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
                    # if the value of key empty, remove the key
                    if row[k] == '':
                        row.pop(k)
                    else:
                        print(k, row[k])
                self.hash[theKey] = row

        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":
    # from roscop import Roscop
    r = Roscop("code_roscop.csv")
    r.read()
    print(r)
    # r.disp('TEMP')
    r.disp('BATH')
