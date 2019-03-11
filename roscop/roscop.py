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

    # call by print()
    def __repr__(self):
        #print("%s:" % row[key],  end='')
        # print()
        return "class Roscop, file: {}".format(self.file)

    # read code roscop file
    def read(self):
        print("Code roscop file: %s" % self.file)
        with open(self.file, 'rt') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                d = db()
                for key in reader.fieldnames:
                    d.key = row[key]
        return


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":
    from roscop import Roscop
    r = Roscop("code_roscop.csv").read()
    print(r)
