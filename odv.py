# ascii.py
# write hdr and data in ascii files

import os
import logging
from re import S
import tools
import numpy as np
from datetime import datetime
    
def writeProfile(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['odv']):
        os.makedirs(cfg['global']['odv'])
    
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing data   file: {}'.format(fileName), end='', flush=True)
    f = open(fileName, 'w')

    # write odv header
    f.write(f"//ODV Spreadsheet file : {fileName}\n")
    f.write(f"//Data treated : {datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
    f.write("//<DataType>Profiles</DataType>\n")
    f.write(f"//<InstrumentType>{cfg[device.lower()]['typeInstrument']}</InstrumentType>\n")
    f.write(f"//<Source>{os.getcwd()}</Sources>\n")
    f.write(f"//<Creator>{cfg['cruise']['CREATOR']}</Creator>\n")
    f.write("//\n")
    f.write("Cruise\tStation\tType\tyyyy-mm-ddThh:mm:ss.sss\tLongitude [degrees_east]\tLatitude [degrees_north]\tBot. Depth [m]")

    # write variables and unit
    for k in fe.keys:
        f.write(f"\t{k} [{fe.roscop[k]['units']}]")
    f.write("\n")

    if cfg[device.lower()] == 'btl':
        type = 'B'
    else:
        type = 'C'
    for i in range(fe.n):
        # for each valid line in array (not _fillvalue)
        
        for m in range(fe.size[i+1]):
            fmt = fe.roscop['PROFILE']['format']
            f.write(f"%s\t{fmt}\t%s" % (cfg['cruise']['CYCLEMESURE'], fe['PROFILE'][i], type))
            f.write(f"\t%s" % (tools.julian2format(fe['TIME'][i], "%Y-%m-%dT%H:%M:%S")))
            fmt = fe.roscop['LONGITUDE']['format']
            f.write(f"\t{fmt}" % (fe['LONGITUDE'][i]))
            fmt = fe.roscop['LATITUDE']['format']
            f.write(f"\t{fmt}" % (fe['LATITUDE'][i]))
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
    print(' done...')

def writeTrajectory(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['odv']):
        os.makedirs(cfg['global']['odv'])
    
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing data   file: {}'.format(fileName), end='', flush=True)
    f = open(fileName, 'w')

    # write odv header
    f.write(f"//ODV Spreadsheet file : {fileName}\n")
    f.write(f"//Data treated : {datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
    f.write("//<DataType>Profiles</DataType>\n")
    f.write(f"//<InstrumentType>{cfg[device.lower()]['typeInstrument']}</InstrumentType>\n")
    f.write(f"//<Source>{os.getcwd()}</Sources>\n")
    f.write(f"//<Creator>{cfg['cruise']['CREATOR']}</Creator>\n")
    f.write("//\n")
    f.write("Cruise\tStation\tType\tyyyy-mm-ddThh:mm:ss.sss\tLongitude [degrees_east]\tLatitude [degrees_north]\tBot. Depth [m]")

    # write variables and unit
    for k in fe.keys:
        if k == 'ID' or k == 'DAYD' or k == 'LATITUDE' or k == 'LONGITUDE':
            continue
        else: 
            f.write(f"\t{k} [{fe.roscop[k]['units']}]")
    f.write("\n")

    type = 'B'

    for i in range(fe.n):
        # Trajectory data of this form have exactly one sample per station. The number of stations
        # equals the number of observation along the trajectory, which is usually large.     
        fmt = "%06d"
        f.write(f"%s\t{fmt}\t%s" % (cfg['cruise']['CYCLEMESURE'], i+1, type))
        f.write(f"\t%s" % (tools.julian2format(fe['DAYD'][i], "%Y-%m-%dT%H:%M:%S")))
        fmt = fe.roscop['LONGITUDE']['format']
        f.write(f"\t{fmt}" % (fe['LONGITUDE'][i]))
        fmt = fe.roscop['LATITUDE']['format']
        f.write(f"\t{fmt}" % (fe['LATITUDE'][i]))
        if fe.iskey('BATH'):
            fmt = fe.roscop['BATH']['format']
            f.write(f"\t{fmt}" % (fe['BATH'][i]))
        else:
            f.write("\t")
        
        for k in fe.keys: 
            if k == 'ID' or k == 'DAYD' or k == 'LATITUDE' or k == 'LONGITUDE':
                continue
            else: 
                if fe[k][i] != fe.roscop[k]['_FillValue']:
                    fmt = fe.roscop[k]['format']
                    f.write(f"\t{fmt}" % (fe[k][i]))
                else:
                    f.write("\t")
        f.write("\n")
    f.close()
    print(' done...')

  

