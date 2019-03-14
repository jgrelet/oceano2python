'''
file_extractor.py
'''
import fileinput


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
        self.__hash = {}
        # constructor build objet by reading the file
        self.read()

    # overloading operators
    def __str__(self):
        ''' overload string representation '''
        return 'Class FileExtractor, file: %s, size = %d' % (self.file, len(self))

   # read code roscop file
    def read(self):
        for line in fileinput.input(
                self.file, openhook=fileinput.hook_encoded("ISO-8859-1")):

            # iterate over the lines of opened file "fileName"
            # ------------------------------------------------
            print(line)


# for testing in standalone context
# ---------------------------------
if __name__ == "__main__":
    fe = FileExtractor('data/cnv/fr29001.cnv')
    fe.read()
