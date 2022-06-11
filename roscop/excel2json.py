#!/usr/bin/env python

from numpy import empty
from xlrd import open_workbook, XLRDError
from collections import OrderedDict
import json
import os
import logging

from version import NAME


class excel:
    """This class convert Mooring instrument in Workbook Excel
     file to an ordered JSON dictionary """

    def __init__(self, abspath):
        """excel constructor from Workbook Excel file name.

        Args:
            abspath (str): absolute path string to Workbook Excel file
        """
        # protected properties with decorators

        self._hash = {} #OrderedDict({})
        # private properties
        self.__logger = logging.getLogger(NAME)
        self.__logger.debug("Pass in excel.init()")
        # call methods
        self.read(abspath)

    def __str__(self):
        """Overload print() method

        Returns:
            str: a JSON dump of the Workbook
        """
        return json.dumps(self._hash, sort_keys=False, indent=4)

    def __getitem__(self, key):
        ''' overloading operators r[key]'''
        if key not in self._hash:
            self.__logger.error(
                f"excel.__getitem__.py: invalid key: \"{key}\"")
        else:
            return self._hash[key]


    @property
    def hash(self):
        """Getter to protected hash dictionary property
       
        Returns:
            OrderedDict: an object as a JSON dictonary
        """
        return self._hash



    def read(self, abspath):

        ws_dict = {} # OrderedDict({})
        row_dict = {} #  OrderedDict({})
        header = {} #OrderedDict({})

        workbook = open_workbook(abspath)
        ws = workbook.sheet_by_name('code_roscop')

        if ws.nrows == 0:
            self.__logger.info("Empty worksheet found.")
            return None

        # store row 1 (column headers)
        hdr = [cell.value for cell in ws.row(0)]
        t = [cell.value for cell in ws.row(1)]

        for i,h in enumerate(hdr):
            header[h] = t[i]
     
        # read each row except header, create dict per row and append to the list
        for row in range(2, ws.nrows):
            #print(ws.cell(row, 0).value)
            #row_dict = {value: ws.cell(row, col).value for col, value in enumerate(header)}
            for col, value in enumerate(header):
                if ws.cell(row, col).value != '':
                    if header[value] == 'numeric':
                        t = float(ws.cell(row, col).value)
                    else:
                        t = str(ws.cell(row, col).value)
                    if value != 'key':
                        row_dict[value] = t
            self._hash[ws.cell(row, 0).value] = row_dict
            row_dict = {}

    def toDict(self):
        """Return python ordered dictionary from JSON string

        Returns:
            OrderedDict: a JSON string representing the worksheet data
        """
        return OrderedDict(json.loads(self.__str__(), object_pairs_hook=OrderedDict))

    def write2json(self, filename, path):
        """Write the Workbook as a JSON file

        Args:
            filename (str): JSON file name
            path (str):  path 

        Returns:
            str: the full path name, none in case of failure 
        """
        # dump list of dict to JSON file
        try:
            json_file = os.path.join(path, filename + '.json')
            with open(json_file, 'w') as json_fd:
                # beautify JSON with indentation
                json.dump(
                    self._hash, json_fd, sort_keys=False, indent=4)
            return json_file
        except FileNotFoundError as ex:
            self.__logger.error(
                f'Something wrong with the path "{path}". Error: {ex}.')
            return None
        except IOError as ex:
            self.__logger.error(
                f'Something wrong happened while saving the file "{filename}.json". Error: {ex}.'
            )
            return None


if __name__ == '__main__':

    from logger import configure_logger
    logger = configure_logger('INFO')
    #logger = configure_logger('DEBUG')
    logger = logging.getLogger(NAME)
    logger.info("Logging OK.")

    r = excel('code_roscop.xls')
    #print(r.hash)
    print(r)
    r.write2json('code_roscop', '.')
    #print(r.toDict())