import argparse
import sys
import myPySimpleGUI as sg
# import PySimpleGUIQt as sg
import toml
import logging
from file_extractor import FileExtractor
import pathlib
from configparser import ConfigParser
import os
import distutils.util as du

# typeInstrument is a dictionary as key: files extension
typeInstrument = {'CTD': 'cnv', 'XBT': 'edf', 'LADCP': 'lad', 'TSG': 'COLCOR'}


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
    > python oceano.py data/cnv/dfr2900[1-3].cnv -d
    > python oceano.py data/cnv/dfr2900[1-3].cnv -k PRES TEMP PSAL DOX2 DENS
    > python oceano.py data/cnv/dfr29*.cnv -d
    '''
    parser = argparse.ArgumentParser(
        description='This program read multiple ASCII file, extract physical parameter \
                following ROSCOP codification at the given column, fill arrays, write header file',
        epilog='J. Grelet IRD US191 - March 2019')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='tests/test.toml')
    parser.add_argument('-i', '--instrument', nargs='?', default=['CTD'],
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP (default: %(default)s)')
    parser.add_argument('-k', '--key', nargs='+', default=['PRES', 'TEMP', 'PSAL'],
                        help='display dictionary for key(s), (default: %(default)s)')
    parser.add_argument('-g', '--gui', action='store_true',
                        help='use GUI interface')
    parser.add_argument('files', nargs='*',
                        help='cnv file(s) to parse, (default: data/cnv/dfr29*.cnv)')
    args = parser.parse_args()

    # initialize filename use to save GUI configuration
    configfile = 'oceano.cfg'

    # set looging mode if debug
    if args.debug:
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # read config Toml file and get the physical parameter, Roscop code
    cfg = toml.load(args.config)
    keys = cfg['split']['ctd'].keys()

    # test arguements from sys.argv, args is never to None with default option set
    if args.gui or len(sys.argv) == 1:

        # change look and feel color scheme
        sg.ChangeLookAndFeel('SandyBeach')

        # define GUI layout
        layout = ([[sg.Text('File(s) to read and convert')],
                   [sg.FilesBrowse(key='_FILE',
                                   tooltip='Choose one or more files',
                                   initial_folder='data/cnv',
                                   file_types=(("cnv files", "*.cnv"),))],
                   [sg.Multiline(size=(30, 5),
                                 key='_MULTI')],
                   # replace the list by typeInstrument.keys()
                   # TODOS
                   [sg.InputCombo(['CTD', 'XBT', 'LADCP', 'TSG'],
                                  key='_INSR', tooltip='Select the instrument')],
                   * [[sg.Checkbox(k, key=k, tooltip='Select the extract the physical parameter {}'.format(k))] for k in keys],
                   [sg.CloseButton('Run'), sg.CloseButton('Cancel')]])

        # create a local instance windows used to reload the saved config from file
        window = sg.Window('Oceano converter').Layout(layout)
        window.LoadFromDisk(configfile)
        window.Finalize
        # display the main windows
        event, values = window.Read()

        # if user close the windows
        if event == None:
            raise SystemExit("Cancelling: user exit")

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

        # values['_FILE'] is a string with files separated by ';' and fileExtractor need a list
        files = values['_FILE'].split(';')
        args.files = files

        # test if a or more file are selected
        if not all(args.files):
            sg.Popup("Cancel", "No filename supplied")
            raise SystemExit("Cancelling: no filename supplied")

        # process of files start here
        fe, n, m = process(args, cfg, 'ctd')

        # display result in popup GUI
        dims = "Dimensions: {} x {}".format(n, m)
        sg.PopupScrolled('Oceano2python', dims,
                         fe.disp(args.key),  size=(80, 40))

        # It will output to a debug window. Bug ? debug windows xas closed before exiting program
        # print = sg.Print
        # or
        # print = sg.Print(size=(80,40))

    else:
        # test if a or more file are selected
        if args.files == []:
            print('You need to specify one or more files to process !!!', end='\n\n')
            parser.print_help(sys.stderr)
            sys.exit(1)
        # in command line mode (console)
        fe, n, m = process(args, cfg, 'CTD')
        print("Dimensions: {} x {}".format(m, n))
        print(fe.disp(args.key))
