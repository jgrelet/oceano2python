import argparse
import sys
import PySimpleGUI as sg
# import PySimpleGUIQt as sg
import toml
import logging
from file_extractor import FileExtractor
import pathlib
from configparser import ConfigParser
import os
import distutils.util as du

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

# initialize program configuration
configfile_name = 'oceano.ini'
# Open or create the configuration file as it doesn't exist yet
config = ConfigParser()
config.optionxform = str
file = config.read(configfile_name)
print(file)

# set looging mode if debug
if args.debug:
    logging.basicConfig(
        format='%(levelname)s:%(message)s', level=logging.DEBUG)

# read config Toml file and get the physical parameter, Roscop code
cfg = toml.load(args.config)
keys = cfg['split']['ctd'].keys()

# test arguements from sys.argv, args is never to None with default option set
if args.gui or args.debug or len(sys.argv) == 1:

    # change look and feel color scheme
    sg.ChangeLookAndFeel('SandyBeach')

    # define GUI layout
    layout = ([[sg.Text('File(s) to read and convert')],
               [sg.FilesBrowse(key='_FILE',
                               initial_folder='data/cnv', file_types=(("cnv files", "*.cnv"),))],
               *[[sg.Checkbox(k, key=k)] for k in keys],
               [sg.CloseButton('Run'), sg.CloseButton('Cancel')]])

    # get a local instance windows use later with Update() method
    window = sg.Window('Oceano converter').Layout(layout)

    # test if configuration file not empty []
    if len(file) != 0:
        # recover the last config setting saved in yaml file and update the windows
        keys = config.options('global')
        for key in keys:
            value = config.get('global', key)
            if key[0] != '_':
                window.FindElement(key).Update(True)

    # create the main windows
    event, values = window.Read()

    # debug return values from GUI
    logging.debug("Event: {}, Values: {}".format(event, values))

    # extract parameters selected (true) from dict values
    new_values = values.copy()
    for k in values.keys():
        if k[0] == '_' or values[k] == False:
            del new_values[k]
    args.key = new_values.keys()

    # values['_FILE'] is a string with files separated by ';' and fileExtractor need a list
    files = values['_FILE'].split(';')
    args.files = files

else:
    # in line command mode
    args.files

# check if no file selected or cancel button pressed
logging.debug("File(s): {}, config: {}, Keys: {}".format(
    args.files, args.config, args.key))
if not all(args.files):
    sg.Popup("Cancel", "No filename supplied")
    raise SystemExit("Cancelling: no filename supplied")

# fileExtractor
fe = FileExtractor(args.files)

cfg = toml.load(args.config)
[n, m] = fe.firstPass()
fe.secondPass(args.key, cfg, 'ctd')
# fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], cdf, 'ctd')
fe.disp(args.key)
# fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])

# save program configuration
config.add_section('global')
for key, value in values.items():
    print(key, value)
    config.set('global', key, str(value))

# save to file
with open(configfile_name, 'w') as cfgfile:
    config.write(cfgfile)
    cfgfile.close()
