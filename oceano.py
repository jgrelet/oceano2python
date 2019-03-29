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

# typeInstrument is a dictionary as key: files extension
typeInstrument = {'CTD': ('cnv', 'CNV'), 'XBT': (
    'EDF', 'edf'), 'LADCP': ('lad', 'LAD'), 'TSG': 'COLCOR'}
ti = typeInstrument  # an alias


def processArgs():
    parser = argparse.ArgumentParser(
        description='This program read multiple ASCII file, extract physical parameter \
                    following ROSCOP codification at the given column, fill arrays, write header file ',
        usage='\npython oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -d\n'
        'python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS\n'
        'python oceano.py data/CTDcnv/dfr29*.cnv -d\n'
        'python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL\n'
        'python oceano.py data/LADCP/*.lad - i LADCP - k DEPTH EWCT NSCT\n'
        ' \n',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('--demo', nargs='?',
                        help='specify the commande line for instrument, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
    parser.add_argument('-i', '--instrument', nargs='?',
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-k', '--key', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
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

    # get all devices
    devices = list(ti.keys())

    # change look and feel color scheme
    sg.ChangeLookAndFeel('SandyBeach')
    frameLayout = {}

    # define a frame layout for each instrument (device)
    for d in devices:
        keys = cfg['split'][d.lower()].keys()
        frameLayout[d] = [* [[sg.Checkbox(k, key=k,
                                          tooltip='Select the extract the physical parameter {}'.format(k))] for k in keys]]
    # for d in devices:
    #    deviceLayout[d] = [sg.Frame(d, frameLayout[d])]

    # define GUI layout
    layout = ([[sg.Text('File(s) to read and convert')],
               [sg.Multiline(size=(40, 5), key='_IN_'),
                sg.Input(key='_HIDDEN_', visible=False,
                         enable_events=True),
                sg.FilesBrowse(key='_HIDDEN_',
                               tooltip='Choose one or more files',
                               initial_folder='data/{}'.format(ti[device][0]))],
               [sg.Combo(list(ti.keys()), enable_events=True, size=(8, 1),
                         key='_COMBO_', tooltip='Select the instrument')],
               # [[sg.Frame(d, frameLayout[d])] for d in devices],
               # for d in devices],
               [sg.Frame('CTD', frameLayout['CTD'], key='_FRAME_CTD', visible=False),
                sg.Frame('XBT', frameLayout['XBT'],
                         key='_FRAME_XBT', visible=False),
                sg.Frame('LADCP', frameLayout['LADCP'],
                         key='_FRAME_LADCP', visible=False),
                sg.Frame('TSG', frameLayout['TSG'], key='_FRAME_TSG', visible=False)],

               [sg.OK(), sg.CloseButton('Cancel')]])
    # [sg.CloseButton('Run'), sg.CloseButton('Cancel')]])

    # create a local instance windows used to reload the saved config from file
    window = sg.Window('Oceano converter').Layout(layout)
    window.LoadFromDisk(configfile)
    window.Finalize
    return window


def updateFilesBrowseCombo(extentions):
    e = window.Rows[1][2]   # hardcoded
    e.FileTypes = []      # init to empty list
    for ext in extentions:
        e.FileTypes.append(("{} files".format(ext), "*.{}".format(ext)))
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
        args.files, args.config, args.key))

    # fileExtractor
    fe = FileExtractor(args.files)

    # cfg = toml.load(args.config)
    [n, m] = fe.firstPass()
    # fe.secondPass(['PRES', 'TEMP', 'PSAL', 'DOX2'], cfg, 'ctd')
    fe.secondPass(args.key, cfg, ti)
    # fe.disp(['PRES', 'TEMP', 'PSAL', 'DOX2'])
    return fe, n, m


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

    # initialize filename use to save GUI configuration
    configfile = 'oceano.cfg'

    # set looging mode if debug
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # read config Toml file and get the physical parameter list (Roscop code) for the specified instrument
    cfg = toml.load(args.config)
    # this the select device from command line !
    device = str(args.instrument)  # convert one element list to str
    if device == 'None':
        print('Missing option --key or -k, key = {}'.format(device))
        print('usage:')
        print(parser.usage)
        sys.exit(0)
    keys = cfg['split'][device.lower()].keys()

    # test arguements from sys.argv, args is never to None with default option set
    if args.gui or len(sys.argv) == 1:

        # setup the GUI windows Layout
        window = defineGUI()
        device = window.FindElement('_COMBO_').DefaultValue
        updateFilesBrowseCombo(ti[device])
        # get all devices

        for d in list(ti.keys()):
            frame = '_FRAME_' + d
            print(frame)
            if d == device:
                print(d)
                window.FindElement(frame).Update(visible=True)

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
                    #raise SystemExit("Cancelling: no filename supplied")
                    continue
                break

            if event is '_COMBO_':
                # you have to go into the bowels of the pygi code, to get the instance of the Combo
                # by the line and column number of the window to update its "fileType" property.
                updateFilesBrowseCombo(ti[values['_COMBO_']])

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
        args.key = new_values.keys()

        # process of files start here
        fe, n, m = process(args, cfg, values['_COMBO_'])

        # display result in popup GUI
        dims = "Dimensions: {} x {}".format(n, m)
        sg.PopupScrolled('Oceano2python', dims,
                         fe.disp(args.key),  size=(80, 40))

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
                print('You need to specify one or more files to process !!!', end='\n\n')
                parser.print_help(sys.stderr)
                sys.exit(1)
        # in command line mode (console)
        fe, n, m = process(args, cfg, device)
        print("Dimensions: {} x {}".format(m, n))
        print(fe.disp(args.key))
