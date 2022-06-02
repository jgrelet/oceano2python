# ascii.py
# write hdr and data in ascii files

import os
import logging
from re import S
import tools
import numpy as np
from datetime import datetime

def writeHeader(cfg, device, dataType):
    '''Specifying * for Type (dataType) lets ODV make the choice. 
    If Bot. Depth values are not available, you should leave this field empty.'''
    if not os.path.exists(cfg['global']['odv']):
        os.makedirs(cfg['global']['odv'])
    
    fileName = "{}/{}_{}_odv.txt".format(cfg['global']['odv'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing data   file: {}'.format(fileName), end='', flush=True)
    fd = open(fileName, 'w')

    # write odv header
    fd.write(f"//ODV Spreadsheet file : {fileName}\n")
    fd.write(f"//Data treated : {datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
    fd.write(f"//<DataType>{dataType}</DataType>\n")
    fd.write(f"//<InstrumentType>{cfg[device.lower()]['typeInstrument']}</InstrumentType>\n")
    fd.write(f"//<Source>{os.getcwd()}</Sources>\n")
    fd.write(f"//<Creator>{cfg['cruise']['CREATOR']}</Creator>\n")
    fd.write("//\n")
    fd.write(f"Cruise\tStation\tType\tyyyy-mm-ddThh:mm:ss.sss\tLongitude [degrees_east]\tLatitude [degrees_north]\tBot. Depth [m]")
    return fd
    
def writeProfile(cfg, device, fe):
   
    # You should use B for stations with less than about 250 samples (e.g., bottle data) and C for stations 
    # with more than about 250 samples (e.g., CTD, XBT, etc.)
    if cfg[device.lower()] == 'btl':
        stationType = 'B'
    else:
        stationType = 'C'

    # write header and return file descriptor
    fd = writeHeader(cfg, device, 'Profiles')
    # write following variables and unit
    for k in fe.keys:
        fd.write(f"\t{k} [{fe.roscop[k]['units']}]")
    fd.write("\n")

    for i in range(fe.n):
        # for each valid line in array (not _fillvalue)
        
        for m in range(fe.size[i+1]):
            fmt = fe.roscop['PROFILE']['format']
            fd.write(f"%s\t{fmt}\t%s" % (cfg['cruise']['CYCLEMESURE'], fe['PROFILE'][i], stationType))
            fd.write(f"\t%s" % (tools.julian2format(fe['TIME'][i], "%Y-%m-%dT%H:%M:%S")))
            fmt = fe.roscop['LONGITUDE']['format']
            fd.write(f"\t{fmt}" % (fe['LONGITUDE'][i]))
            fmt = fe.roscop['LATITUDE']['format']
            fd.write(f"\t{fmt}" % (fe['LATITUDE'][i]))
            if fe.iskey('BATH') and not np.isnan(fe['BATH'][i]):
                fmt = fe.roscop['BATH']['format']
                fd.write(f"\t{fmt}" % (fe['BATH'][i]))
            else:
                fd.write("\t")
            for k in fe.keys:       
                if not np.isnan(fe[k][i][m]):
                #if fe[k][i][m] != fe.roscop[k]['_FillValue']:
                    fmt = fe.roscop[k]['format']
                    fd.write(f"\t{fmt}" % (fe[k][i][m]))
                else:
                    fd.write("\t")
            fd.write("\n")
    fd.close()
    print(' done...')

def writeTrajectory(cfg, device, fe):
    
    # write header and return file descriptor
    fd = writeHeader(cfg, device, 'Trajectories')
    # write variables and unit
    for k in fe.keys:
        if k == 'ID' or k == 'DAYD' or k == 'LATITUDE' or k == 'LONGITUDE':
            continue
        else: 
            fd.write(f"\t{k} [{fe.roscop[k]['units']}]")
    fd.write("\n")

    # If Bot. Depth values are not available, you should leave this field empty, 
    # usually the case for trajectory
    stationType = ''

    for i in range(fe.n):
        # Trajectory data of this form have exactly one sample per station. The number of stations
        # equals the number of observation along the trajectory, which is usually large.     
        fmt = "%06d"
        fd.write(f"%s\t{fmt}\t%s" % (cfg['cruise']['CYCLEMESURE'], i+1, stationType))
        fd.write(f"\t%s" % (tools.julian2format(fe['DAYD'][i], "%Y-%m-%dT%H:%M:%S")))
        fmt = fe.roscop['LONGITUDE']['format']
        fd.write(f"\t{fmt}" % (fe['LONGITUDE'][i]))
        fmt = fe.roscop['LATITUDE']['format']
        fd.write(f"\t{fmt}" % (fe['LATITUDE'][i]))
        if fe.iskey('BATH') and not np.isnan(fe['BATH'][i]):
            fmt = fe.roscop['BATH']['format']
            fd.write(f"\t{fmt}" % (fe['BATH'][i]))
        else:
            fd.write("\t")
        
        for k in fe.keys: 
            if k == 'ID' or k == 'DAYD' or k == 'LATITUDE' or k == 'LONGITUDE':
                continue
            else: 
                if fe[k][i] != fe.roscop[k]['_FillValue']:
                    fmt = fe.roscop[k]['format']
                    fd.write(f"\t{fmt}" % (fe[k][i]))
                else:
                    fd.write("\t")
        fd.write("\n")
    fd.close()
    print(' done...')

  

