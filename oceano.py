#!/usr/bin/env python

# https://github.com/jgrelet/oceano2python

import argparse
import sys
import toml
import logging
from profile import Profile
from trajectory import Trajectory
from pathlib import Path
from glob import glob
from physical_parameter import Roscop
import os.path as path
from __init__ import __version__, __date__, __author__

# todo: move type_of_data and typeInstrument to config.toml
type_of_data = {'PROFILE': ['CTD', 'BTL','XBT','LADCP','RBR', 'MVP'], 'TRAJECTORY': ['TSG','COLCOR','MTO', 'CASINO']}

# typeInstrument is a dictionary as key: files extension
typeInstrument =   {'CTD': ('cnv', 'CNV'), 
                    'XBT': ('EDF', 'edf'), 
                    'LADCP': ('lad', 'LAD'), 
                    'RBR': ('txt', 'TXT', 'rbr'),
                    'MVP': ('txt', 'TXT', 'm1'),
                    'COLCOR': ('colcor','COLCOR'), 
                    'TSG': ('cnv','CNV'),
                    'CASINO': ('csv'),
                    'BTL': ('btl', 'BTL')}

ti = typeInstrument  # an alias

# initialize filename use to save GUI configuration
configfile = 'oceano.cfg'
# default file name for ROSCOP csv
defaultRoscop = 'code_roscop.csv'

def processArgs():
    # get the path to the module oceano2python, use to file defaut roscop_code
    roscop_file_path = path.dirname(path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description='This program read multiple ASCII file, extract physical parameter \
                    following ROSCOP codification at the given column, fill arrays, write header file ',
        usage='\npython oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -d\n'
        'python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS\n'
        'python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -d\n'
        'python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL\n'
        'python oceano.py data/LADCP/*.lad -i LADCP -k DEPTH EWCT NSCT\n'
        'python oceano.py data/CTD/btl/fr290*.btl -i BTL -k BOTL PRES DEPTH ETDD TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2'
        ' \n',
        epilog='J. Grelet IRD US191 - March 2019 / Feb 2020')
    parser.add_argument('-v', '--version', help='display version number',
                        action='version', version=f'%(prog)s  v{__version__} - {__author__} - {__date__} ')
    parser.add_argument('-d', '--debug', help='display debug informations',
                        action='store_true')
    parser.add_argument('-c', '--config', help="toml configuration file, (default: %(default)s)",
                        default='config.toml')
    parser.add_argument('-i', '--instrument', nargs='?', choices=ti.keys(),
                        help='specify the instrument that produce files, eg CTD, XBT, TSG, LADCP')
    parser.add_argument('-r', '--roscop', nargs='?',
                        help="specify location and ROSCOP file name,  (default: %(default)s)",
                        default=roscop_file_path +'/code_roscop.csv')
    parser.add_argument('-k', '--keys', nargs='+',
                        help='display dictionary for key(s), (default: %(default)s)')
    parser.add_argument('--database', help='save sqlite3 database in test.db instead of memory',
                        action='store_true')
    # type=argparse.FileType('r') don't work with under DOS 
    parser.add_argument('files', nargs='*',
                        help='ASCII file(s) to parse')                        
    return parser


if __name__ == "__main__":
    '''
    usage:
    > python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD
    > python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -k PRES TEMP PSAL DOX2 DENS -d
    > python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS
    > python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -d
    > python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL
    > python oceano.py data/LADCP/*.lad -i LADCP - k DEPTH EWCT NSCT
    > python oceano.py data/CTD/btl/fr290*.btl -i BTL -k BOTL PRES DEPTH ETDD TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2
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

    # get roscop file
    if cfg['global']['codeRoscop'] != None:
        defaultRoscop = Path(cfg['global']['codeRoscop'])
    if args.roscop != None:
        defaultRoscop = args.roscop
    roscop = Roscop(defaultRoscop)

    # test if the file exist from command line
    if args.files == []:
        print(
            'Error, you need to specify one or more files to process !!!', end='\n\n')
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    # retreive files list from command line, works under DOS, Git bash and Linux
    files = []
    for file in args.files:  
        files += glob(file)  
    args.files = files

    # device (instrument) is mandatory
    if device == 'None':
        print(
            'Error: missing option -i or --instrument, instrument = {}\n'.format(device))
        parser.print_help(sys.stderr)
        sys.exit(1)

    # return the type of data, eg PROFILE or TRAJECTORY from device
    def search_dict(type_of_data, instrument):
        for k,i in type_of_data.items():
            if instrument in i:
                return(k)

    # get the type of data, eg PROFILE or TRAJECTORY
    type = search_dict(type_of_data, args.instrument)
    logging.debug(type)

    # call the right object
    if type == 'PROFILE':
        context = Profile(args.files, roscop, args.keys)
    elif type == 'TRAJECTORY':
        context = Trajectory(args.files, roscop, args.keys)
    else:
        print(f"Invalide type: {type}")
        sys.exit(1)
        
    # start processing
    context.process(args, cfg, device)
    
    

