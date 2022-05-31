# ascii.py
# write hdr and data in ascii files

import os
import logging
from re import S
import tools
import numpy as np
from datetime import datetime
    
def writeDataProfile(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    # write header, first line
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['PI']))

    # write odv header
    f.write(f"//ODV Spreadsheet file : {dataFile}\n")
    f.write(f"//Data treated : {datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
    f.write("//<DataType>Profiles</DataType>\n")
    f.write(f"//<InstrumentType>{cfg[device]['typeInstrument']}</InstrumentType>\n")
    f.write(f"//<Source>{os.getcwd()}</Sources>\n")
    f.write(f"//<Creator>{cfg['cruise']['CREATOR']}</Creator>\n")
    f.write("//\n")
    f.write("Cruise\tStation\tType\tyyyy-mm-ddThh:mm:ss.sss\tLongitude [degrees_east]\tLatitude [degrees_north]\tBot. Depth [m]")

    # write variables and unit
    for k in fe.keys:
        f.write(f"\t{k} [{fe.roscop[k]['units']}]")
    f.write("\n")

    type = 'C'
    for i in range(fe.n):
        # for each valid line in array (not _fillvalue)
        
        for m in range(fe.size[i+1]):
            fmt = fe.roscop['PROFILE']['format']
            f.write(f"%s\t{fmt}\t%s" % (cfg['cruise']['CYCLEMESURE'], fe['PROFILE'][i], type))
            f.write(f"\t%s" % (tools.julian2format(fe['TIME'][i], "%Y-%m-%dT%H:%M:%S")))
            f.write(f"\t%f" % (fe['LONGITUDE'][i]))
            f.write(f"\t%f" % (fe['LATITUDE'][i]))
            if fe.iskey('BATH'):
                fmt = fe.roscop['BATH']['format']
                f.write(f"\t{fmt}" % (fe['BATH'][i]))
            else:
                f.write("\t")
            for k in fe.keys:        
                if fe[k][i][m] != fe.roscop[k]['_FillValue']:
                    fmt = fe.roscop[k]['format']
                    f.write(f"\t{fmt}" % (fe[k][i][m]))
                else:
                    f.write("\t")
            f.write("\n")
    f.close()

def writeProfile(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['odv']):
        os.makedirs(cfg['global']['odv'])
    
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing data   file: {}'.format(fileName), end='', flush=True)
    writeDataProfile(fileName, cfg, device.lower(), fe, r)
    print(' done...')

def writeDecimalDataTrajectory(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    # write header, first line
    f.write("{}  {}  {}  ".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE']))
    if 'typeInstrument' in cfg[device]:
        f.write(f"{cfg[device]['typeInstrument']}")
    if 'instrumentNumber' in cfg[device]:
        f.write(f"{cfg[device]['instrumentNumber']}")
    if 'PI' in cfg['cruise']:
        f.write(f"{cfg['cruise']['PI']}")
    f.write("\n")

    # write header, second line with physical parameter liste, fill with N/A if necessary
    for k in fe.keys:
        f.write(f"  {k}  ")
    f.write("\n")
    # write data
    for n in range(fe.n):
        for k in fe.keys: 
            fmt = fe.roscop[k]['format']
            if '_FillValue' in fe.roscop[k] and fe[k][n] == fe.roscop[k]['_FillValue']:
                f.write('  1e+36 ')
            else:
                f.write(f" {fmt} " % (fe[k][n]))
        f.write("\n")
    f.close()

def writeHumanDataTrajectory(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    # write header, first line
    f.write("{}  {}  {}  ".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE']))
    if 'typeInstrument' in cfg[device]:
        f.write(f"{cfg[device]['typeInstrument']}")
    if 'instrumentNumber' in cfg[device]:
        f.write(f"{cfg[device]['instrumentNumber']}")
    if 'PI' in cfg['cruise']:
        f.write(f"{cfg['cruise']['PI']}")
    f.write("\n")

    # write header, second line with physical parameter liste, fill with N/A if necessary
    for k in fe.keys:
        if k == 'DAYD':
            f.write("    DATE      TIME   ")
            continue
        f.write(f"   {k}  ")
    f.write("\n")
    # write data
    for n in range(fe.n):
        for k in fe.keys: 
            if k == 'LATITUDE':
                f.write(f" {tools.Dec2dmc(fe[k][n],'N')} ")
                continue
            if k == 'LONGITUDE':
                f.write(f" {tools.Dec2dmc(fe[k][n],'E')} ")
                continue
            if k == 'DAYD':
                # use the format given in devide trajectory toml config file
                dt = tools.julian2format(fe[k][n])
                f.write(f" {dt} ")
                continue
            fmt = fe.roscop[k]['format']
            if '_FillValue' in fe.roscop[k] and fe[k][n] == fe.roscop[k]['_FillValue']:
                f.write('  1e+36 ')
            else:
                f.write(f" {fmt} " % (fe[k][n]))
        f.write("\n")
    f.close()


def writeTrajectory(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['odv']):
        os.makedirs(cfg['global']['odv'])
    
    # write ascii file with human read time and position
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing file: {}'.format(fileName), end='', flush=True)
    writeHumanDataTrajectory(fileName, cfg, device.lower(), fe, r, )
    print(' done...')
    
    # write ascii file with decimal time and position
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing file: {}'.format(fileName), end='', flush=True)
    writeDecimalDataTrajectory(fileName, cfg, device.lower(), fe, r)
    print(' done...')
   