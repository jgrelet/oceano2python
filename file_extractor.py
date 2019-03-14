'''
file_extractor.py
'''
import fileinput
import toml


class FileExtractor:

    '''
    This class read an ASCII file, extract physical parameter with ROSCOP codification from the given column
    '''

    # constructor with values by default
    def __init__(self, file):
        # attibutes
        # public:
        self.file = file
        # private:
        self.__headeer = {}
        self.__data = {}
        # constructor build objet by reading the file

    # overloading operators

    def __str__(self):
        ''' overload string representation '''
        return 'Class FileExtractor, file: %s, size = %d' % (self.file, len(self))

   # read code roscop file
    def read(self, keys, dic):
        for line in fileinput.input(
                self.file, openhook=fileinput.hook_encoded("ISO-8859-1")):
            if line[0] == '#' or line[0] == '*':
                continue

            # iterate over the lines of opened file "fileName"
            # ------------------------------------------------
            p = line.split()
            for k in keys:
                print("{} ".format(p[dic[k]]), end='')
            print()


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":
    fe = FileExtractor('data/cnv/fr29001.cnv')
    cfg = toml.load('tests/test.toml')
    dic = cfg['split']['ctd']
    fe.read(['PRES', 'TEMP', 'PSAL', 'DOX2'], dic)
