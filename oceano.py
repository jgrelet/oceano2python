import argparse
import sys
import PySimpleGUIQt as sg
# import PySimpleGUIQt as sg
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

# set looging mode if debug
if args.debug:
    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=logging.DEBUG)

# test arguements from sys.argv, args is never to None with default option set
if len(sys.argv) == 1:
    # define GUI layout
    layout = ([[sg.Text('File(s) to read and convert')],
               [sg.Input(size=(40, 1)), sg.FileBrowse()],
               [sg.Checkbox('PRES'), sg.Checkbox('TEMP'), sg.Checkbox('PSAL')],
               [sg.CloseButton('Run'), sg.CloseButton('Cancel')]])

    # create the main windows
    event, values = sg.Window('Oceano converter').Layout(layout).Read()

    # fname = pathlib.PurePosixPath(fname)
    print(event, values[0])


else:
    # in line command
    values[0] = args.files

if not values[0]:
    sg.Popup("Cancel", "No filename supplied")
    raise SystemExit("Cancelling: no filename supplied")
# transform full pathname into list
fe = FileExtractor([values[0]])
print("File(s): {}, Config: {}".format(values[0], args.config))

cfg = toml.load(args.config)
[n, m] = fe.firstPass()
print("Indices:", n, m)
fe.secondPass(args.key, cfg, 'ctd')
# fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], cdf, 'ctd')
fe.disp(args.key)
# fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])
