#!/usr/bin/env python

import argparse
import logging
import os.path as path
import sys
from glob import glob
from pathlib import Path

import toml

from oceano2python import __author__, __date__, __version__
from oceano2python.core.config_validation import validate_runtime_config
from oceano2python.core.profile import Profile
from oceano2python.core.trajectory import Trajectory
from oceano2python.metadata.physical_parameter import Roscop


type_of_data = {
    "PROFILE": ["CTD", "BTL", "XBT", "LADCP", "RBR", "MVP"],
    "TRAJECTORY": ["TSG", "COLCOR", "MTO", "CASINO"],
}

typeInstrument = {
    "CTD": ("cnv", "CNV"),
    "XBT": ("EDF", "edf"),
    "LADCP": ("lad", "LAD"),
    "RBR": ("txt", "TXT", "rbr"),
    "MVP": ("txt", "TXT", "m1"),
    "COLCOR": ("colcor", "COLCOR"),
    "TSG": ("cnv", "CNV"),
    "CASINO": ("csv"),
    "BTL": ("btl", "BTL"),
}

ti = typeInstrument
configfile = "oceano.cfg"
defaultRoscop = "code_roscop.csv"


def processArgs():
    roscop_file_path = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description="This program read multiple ASCII file, extract physical parameter \
                    following ROSCOP codification at the given column, fill arrays, write header file ",
        usage="\npython oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -d\n"
        "python oceano.py data/CTD/cnv/dfr2900[1-3].cnv -i CTD -k PRES TEMP PSAL DOX2 DENS\n"
        "python oceano.py data/CTD/cnv/dfr29*.cnv -i CTD -d\n"
        "python oceano.py data/XBT/T7_0000*.EDF -i XBT -k DEPTH TEMP SVEL\n"
        "python oceano.py data/LADCP/*.lad -i LADCP -k DEPTH EWCT NSCT\n"
        "python oceano.py data/CTD/btl/fr290*.btl -i BTL -k BOTL PRES DEPTH ETDD TE01 TE02 PSA1 PSA2 DO11 DO12 DO21 DO22 FLU2"
        " \n",
        epilog="J. Grelet IRD US191 - March 2019 / Feb 2020",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="display version number",
        action="version",
        version=f"%(prog)s  v{__version__} - {__author__} - {__date__} ",
    )
    parser.add_argument("-d", "--debug", help="display debug informations", action="store_true")
    parser.add_argument(
        "-c",
        "--config",
        help="toml configuration file, (default: %(default)s)",
        default="config.toml",
    )
    parser.add_argument(
        "-i",
        "--instrument",
        nargs="?",
        choices=ti.keys(),
        help="specify the instrument that produce files, eg CTD, XBT, TSG, LADCP",
    )
    parser.add_argument(
        "-r",
        "--roscop",
        nargs="?",
        help="specify location and ROSCOP file name,  (default: %(default)s)",
        default=str(roscop_file_path / "code_roscop.csv"),
    )
    parser.add_argument(
        "-k", "--keys", nargs="+", help="display dictionary for key(s), (default: %(default)s)"
    )
    parser.add_argument(
        "--database", help="save sqlite3 database in test.db instead of memory", action="store_true"
    )
    parser.add_argument("files", nargs="*", help="ASCII file(s) to parse")
    return parser


def search_dict(mapping, instrument):
    for key, instruments in mapping.items():
        if instrument in instruments:
            return key
    return None


def main(argv=None):
    parser = processArgs()
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

    cfg = toml.load(args.config)
    device = str(args.instrument)

    roscop_file = defaultRoscop
    if cfg["global"]["codeRoscop"] is not None:
        roscop_file = Path(cfg["global"]["codeRoscop"])
    if args.roscop is not None:
        roscop_file = args.roscop
    roscop = Roscop(roscop_file)

    if args.files == []:
        print("Error, you need to specify one or more files to process !!!", end="\n\n")
        parser.print_help(sys.stderr)
        return 1

    files = []
    for file in args.files:
        files += glob(file)
    args.files = files

    if device == "None":
        print(f"Error: missing option -i or --instrument, instrument = {device}\n")
        parser.print_help(sys.stderr)
        return 1

    data_type = search_dict(type_of_data, args.instrument)
    logging.debug(data_type)
    validate_runtime_config(cfg, device, data_type, args.keys)

    if data_type == "PROFILE":
        context = Profile(args.files, roscop, args.keys)
    elif data_type == "TRAJECTORY":
        context = Trajectory(args.files, roscop, args.keys)
    else:
        print(f"Invalide type: {data_type}")
        return 1

    context.process(args, cfg, device)
    return 0


if __name__ == "__main__":
    sys.exit(main())
