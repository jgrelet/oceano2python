import argparse
import sys
# import myPySimpleGUI as sg
import PySimpleGUI as sg
import toml
import logging
from file_extractor import FileExtractor
import pathlib
from configparser import ConfigParser
import os
import distutils.util as du
import netcdf

# typeInstrument is a dictionary as key: files extension
typeInstrument = {'CTD': ('cnv', 'CNV'), 'XBT': (
    'EDF', 'edf'), 'LADCP': ('lad', 'LAD'), 'TSG': 'COLCOR'}
variables_1D = ['TIME', 'LATITUDE', 'LONGITUDE']
ti = typeInstrument  # an alias
filesBrowsePosition_row = 2
filesBrowsePosition_column = 1

# initialize filename use to save GUI configuration
configfile = 'oceano.cfg'

def processArgs():
    parser = argparse.ArgumentParser(
        description='This program read multiple ASCII file, extract physical parameter \
                    following ROSCOP codification at the given column, fill arrays, write header file ',
        usage='\npython oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -d\n'
        'python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS\n'
        'python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -d\n'
        'python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL\n'
        'python oceano.py data/LADCP/*.lad - i LADCP - k DEPTH EWCT NSCT\n'
        ' \n',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('--demo', nargs='?', choices=ti.keys(),
                        help='specify the commande line for instrument, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
    parser.add_argument('-i', '--instrument', nargs='?', choices=ti.keys(),
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-k', '--keys', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
                        help='display dictionary for key(s), (default: %(default)s)')
    parser.add_argument('-g', '--gui', action='store_true',
                        help='use GUI interface')
    parser.add_argument('files', nargs='*', type=argparse.FileType('r', encoding='ISO-8859-1'),
                        help='ASCII file(s) to parse')
    return parser

# TODOS:
# DEPTH is missing
# file name is not clear at startup
# if no file selected, don't leave the program


def defineGUI():

    # check if GUI config file exist
    if args.instrument != None:
        instrument_default_value = args.instrument
    else:
        instrument_default_value = 'CTD'

    # get all devices
    devices = list(ti.keys())

    # change look and feel color scheme
    sg.ChangeLookAndFeel('SandyBeach')
    frameLayout = {}

    # define a frame layout for each instrument (device)
    for d in devices:
        keys = cfg['split'][d.lower()].keys()
        # List comprehensions
        frameLayout[d] = [[sg.Checkbox(k, key=k,
                                          tooltip='Select the extract the physical parameter {}'.format(k))] for k in keys]

    # define GUI layout
    layout = ([[sg.Text('File(s) to read and convert')],                              # row 0
               [sg.Multiline(size=(40, 5), key='_IN_'),                               # row 1, col 0
                sg.Input(key='_HIDDEN_', visible=False,                               # row 1, col 1
                         enable_events=True),
                sg.FilesBrowse(key='_HIDDEN_', initial_folder=None,                   # row 1, col 2
                               tooltip='Choose one or more files')],    
               [sg.Combo(list(ti.keys()), enable_events = True, size=(8, 1),          # row 2
                         default_value = instrument_default_value,                    
                         key='_COMBO_', tooltip='Select the instrument')],
               [sg.Frame(d, frameLayout[d], key='_FRAME_{:s}'.format(d) , visible=True)          # row 3
                for d in devices],                                                    
               [sg.OK(), sg.CloseButton('Cancel')]])                                  # row 4
               # [sg.CloseButton('Run'), sg.CloseButton('Cancel')]])

    # create a local instance windows used to reload the saved config from file
    window = sg.Window('Oceano converter').Layout(layout)
    window.LoadFromDisk(configfile)
    window.Finalize
    return window 


def updateFilesBrowseCombo(extentions, x, y):
    '''# special function used to update the FilesBrowseCombo with canvas poisition
    # instead of key because the same key is assign to shadow input object
    '''
    e = window.Rows[x][y]    # hardcoded
    e.FileTypes = []         # init to empty list
    for ext in extentions:
        e.FileTypes.append(("{} files".format(ext), "*.{}".format(ext)))

    e.initial_folder = 'data/{}'.format(extentions[0])
    window.Finalize


def process(args, cfg, ti):
    '''
    Extract data from ASCII files and return FileExtractor instannce and array size of extracted data

    Parameters
    ----------
        args : ConfigParser
        cfg : dict
            toml instance describing the file structure to decode
        ti : str {'CNV', 'XBT','LADCP','TSG',}
            The typeInstrument key

    Returns
    -------
        fe: FileExtractor
        n, m: array size
    '''

    # check if no file selected or cancel button pressed
    logging.debug("File(s): {}, config: {}, Keys: {}".format(
        args.files, args.config, args.keys))

    # fileExtractor
    fe = FileExtractor(args.files, args.keys)

    fe.set_regex(cfg, ti)
    
    # cfg = toml.load(args.config)
    fe.first_pass()
    # fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], cfg, 'ctd')
    fe.second_pass(cfg, ti, variables_1D)
    # fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])
    return fe


if __name__ == "__main__":
    '''
    usage:
    > python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -d
    > python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -k PRES TEMP PSAL DOX2 DENS
    > python oceano.py data/CTD/cnv/dfr29*.cnv -d
    '''
    # recover and process line arguments
    parser = processArgs()
    args = parser.parse_args()

    # set looging mode if debug
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # read config Toml file and get the physical parameter list (Roscop code) for the specified instrument
    cfg = toml.load(args.config)
    # this the select device from command line !
    device = str(args.instrument)  # convert one element list to str

    # test arguements from sys.argv, args is never to None with default option set
    if args.gui or len(sys.argv) == 1:

        # setup the GUI windows Layout
        window = defineGUI()
        device = window.FindElement('_COMBO_').DefaultValue
        keys = cfg['split'][device.lower()].keys()
        # can't update combo with FindElement('_HIDDEN_').Update(), we use this function
        # with hardcoded FilesBrowseCombo position
        updateFilesBrowseCombo(
            ti[device], filesBrowsePosition_column, filesBrowsePosition_row)

        # set the rigth frame for device visible, dosn't work
        #  File "C:\git\python\PySimpleGUI\PySimpleGUI.py", line 2362, in Update
        #  self.TKFrame.pack()
        #  AttributeError: 'NoneType' object has no attribute 'pack'
        # for d in list(ti.keys()):
        #     print(d)
        #     if d == device:
        #         window.FindElement(
        #             '_FRAME_{:s}'.format(d)).Update(visible=True)

        # main GUI loop
        while True:
           # display the main windows
            event, values = window.Read()
            print(event, values)

            if event is 'Cancel' or event == None:
                raise SystemExit("Cancelling: user exit")

            if event is 'OK':  # end of initialization, process data now
                # values['_HIDDEN_'] is a string with files separated by ';' and fileExtractor need a list
                files = values['_HIDDEN_'].split(';')
                args.files = files

                # test if a or more file are selected
                if not all(args.files):
                    sg.Popup("Cancel", "No filename supplied")
                    # raise SystemExit("Cancelling: no filename supplied")
                    continue
                break

            if event is '_COMBO_':
                # you have to go into the bowels of the pygi code, to get the instance of the Combo
                # by the line and column number of the window to update its "fileType" property.
                updateFilesBrowseCombo(
                    ti[values['_COMBO_']], filesBrowsePosition_column, filesBrowsePosition_row)

            # update the Multilines instance from FilesBrowse return
            if event is '_HIDDEN_':
                window.Element('_IN_').Update(
                    values['_HIDDEN_'].split(';'))

        # save program configuration
        window.SaveToDisk(configfile)

        # debug return values from GUI
        logging.debug("Event: {}, Values: {}".format(event, values))

        # extract selected parameters (true) from dict values
        new_values = values.copy()
        for k in values.keys():
            if k[0] == '_' or values[k] == False:
                del new_values[k]
        args.keys = new_values.keys()

        # process of files start here
        fe = process(args, cfg, values['_COMBO_'])

        # display result in popup GUI
        dims = "Dimensions: {} x {}".format(fe.n, fe.m)
        sg.PopupScrolled('Oceano2python', dims,
                         fe.disp(),  size=(80, 40))

        # It will output to a debug window. Bug ? debug windows xas closed before exiting program
        # print = sg.Print
        # or
        # print = sg.Print(size=(80,40))

    else:
        # demo mode, only in command line
        if args.demo != None:
            print('demo mode: {}'.format(args.demo))
            sys.exit(1)
        # test if a or more file are selected
        else:
            if args.files == []:
                print(
                    'Error, you need to specify one or more files to process !!!', end='\n\n')
                parser.print_help(sys.stderr)
                sys.exit(1)
            else:
                files = []
                for f in args.files:
                    files.append(f.name)
                args.files = files
        if device == 'None':
            print(
                'Error: missing option -i or --instrument, instrument = {}\n'.format(device))
            parser.print_help(sys.stderr)
            sys.exit(1)

        keys = cfg['split'][device.lower()].keys()
        # in command line mode (console)
        fe = process(args, cfg, device)
        #print("Dimensions: {} x {}".format(fe.m, fe.n))
        #print(fe.disp())
        netcdf.writeNetCDF( 'output/test.nc', fe,variables_1D)
