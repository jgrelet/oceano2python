import argparse
import sys
import PySimpleGUI as sg
import toml
import logging
from file_extractor import FileExtractor
import pathlib

# usage:
# > python oceano.py data/cnv/dfr2900[1-3].cnv -d
# > python oceano.py data/cnv/dfr2900[1-3].cnv -k PRES TEMP PSAL DOX2 DENS
# > python oceano.py data/cnv/dfr29*.cnv -d
parser = argparse.ArgumentParser(
    description='This program read multiple ASCII file, extract physical parameter \
            following ROSCOP codification at the given column, fill arrays, write header file',
    epilog='J. Grelet IRD US191 - March 2019')
parser.add_argument('-d', '--debug', help='display debug informations',
                    action='store_true')
parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                    default='tests/test.toml')
parser.add_argument('-k', '--key', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
                    help='display dictionary for key(s), (default: %(default)s)')
parser.add_argument('-g', '--gui', action='store_true',
                    help='use GUI interface')
parser.add_argument('files', nargs='*',
                    help='cnv file(s) to parse, (default: data/cnv/dfr29*.cnv)')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=logging.DEBUG)


# test arguements from sys.argv, args is never to None with default option set
if len(sys.argv) == 1:
    event, fname = sg.Window('My Script').Layout([[sg.Text('Document to open')],
                                                  [sg.In(), sg.FileBrowse()],
                                                  [sg.CloseButton('Open'), sg.CloseButton('Cancel')]]).Read()
    #fname = pathlib.PurePosixPath(fname)
    print(event, fname)


else:
    fname = args.files

if not fname:
    sg.Popup("Cancel", "No filename supplied")
    raise SystemExit("Cancelling: no filename supplied")
fe = FileExtractor(fname)
print("File(s): {}, Config: {}".format(fname, args.config))

cfg = toml.load(args.config)
[n, m] = fe.firstPass()
print("Indices:", n, m)
fe.secondPass(args.key, cfg, 'ctd')
# fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], cdf, 'ctd')
fe.disp(args.key)
# fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])
