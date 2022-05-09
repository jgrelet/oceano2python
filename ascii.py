# ascii.py
# write hdr and data in ascii files

import os
import logging
import tools
import numpy as np
from datetime import datetime
    
def writeHeaderProfile(hdrFile, cfg, device, fe, r):
    f = open(hdrFile, 'w')
    # first line, header ex: 
    # PIRATA-FR30  THALASSA  IRD  SBE911+  09P-1263  BOURLES
    print("{}  {}  {}  {}  {}  {}".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['PI']))
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['PI']))
    # write next lines, start and end profile ex: 
    # 00001 18/02/2020 19:04:19 18/02/2020 22:41:07 11°28.85 N 023°00.59 W  4063  5083 fr30001
    # add PROFILE and END_PROFILE_TIME, BATH
    for i in range(fe.n):
        for k in fe.variables_1D:
            if k == 'TIME':
                t = tools.julian2format(fe['TIME'][i])
                print(f"{t}  ", end='')
                f.write(f"{t}  ")
                #query = self.db.query('SELECT end_date_time FROM station')
                # need to cast <class 'numpy.int32'> to int 
                query = fe.db.select('station', ['end_date_time', 'filename'], station = int(fe['PROFILE'][i]))
                for idx, item in enumerate(query):
                    dt = item['end_date_time']
                    if dt == None:
                        pass
                    else:
                        print(f"{dt}  ", end='')
                        f.write(f"{dt}  ")
                    filename = item['filename']

            elif k == 'LATITUDE':
                lat = tools.Dec2dmc(fe['LATITUDE'][i],'N')
                print(f"{lat}  ", end='')
                f.write(f"{lat}  ")
            elif k == 'LONGITUDE':
                lon = tools.Dec2dmc(fe['LONGITUDE'][i],'W')
                print(f"{lon}  ", end='')
                f.write(f"{lon}  ")
            else:
                fmt = fe.roscop[k]['format']
                if np.isnan(fe[k][i]):  # a revoir !!!
                    #print(k, type(fe[k][i]))
                    print(' 1e+36 ', end='')
                    f.write(' 1e+36 ')
                else:
                    print(f"{fmt}  " % (fe[k][i]), end='')
                    f.write(f"{fmt}  " % (fe[k][i]))

        # get max value for each profile, DEPTH or PRES is the first value => keys[0]
        col = f"MAX({fe.keys[0]})"
        query = fe.db.query(
            f"SELECT {col} FROM data WHERE station_id = {i}")
        for idx, item in enumerate(query):
            dt = item[col]
            if dt == None:
                print(' 1e+36 ', end='')
                f.write(' 1e+36 ')
            else:
                print("%6.1f  " % (item[col]), end='')
                f.write("%6.1f  " % (item[col]))
        print(f" {filename}", end = '\n')
        f.write(f" {filename}\n")
      
    f.close()
    
    
def writeDataProfile(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    # write header, first line
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['CYCLEMESURE'], 
        cfg['cruise']['PLATEFORME'], cfg['cruise']['INSTITUTE'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['PI']))

    # write header, second line with physical parameter liste, fill with N/A if necessary
    f.write("PROFILE  ")
    for k in fe.keys:
        f.write(f"  {k} ")
    for r in range(len(fe.keys),len(fe.variables_1D)+1):
        f.write('   N/A  ')
    f.write("\n")

     # write station or profile header
    for i in range(fe.n):
        # write header (pres or depth = -1)
        for k in fe.variables_1D:
            fmt = fe.roscop[k]['format']
            if k == 'PROFILE' or k == 'PRFL':
                f.write(f"{fmt}       -1 " % (fe[k][i]))
            elif k == 'TIME':
                # save date in EPIC format (numeric) in profile header
                f.write(f" {fmt} {'%s'}" % (fe[k][i] - fe.julian_from_year, 
                    tools.julian2format(fe[k][i], "%Y%m%d%H%M%S")))
            else:
                if np.isnan(fe[k][i]):
                    #print(k, type(fe[k][i]))
                    f.write(' 1e+36 ')
                else:
                    f.write(f" {fmt} " % (fe[k][i]))
        # fill last header columns with 1e+36 if
        for r in range(len(fe.variables_1D)+1, len(fe.keys)):
                    f.write(' 1e+36 ')
        f.write("\n")

        # for each valid line in array (not _fillvalue)
        for m in range(fe.m):
            # don't print line if data is _fillValue
            if fe[fe.keys[0]][i][m] != fe.roscop[fe.keys[0]]['_FillValue']:
                fmt = fe.roscop['PROFILE']['format']
                f.write(f"{fmt}  " % (fe['PROFILE'][i]))
                # add value for each parameter, use format from roscop
                for k in fe.keys:        
                    fmt = fe.roscop[k]['format']
                    f.write(f" {fmt} " % (fe[k][i][m]))
                for r in range(len(fe.keys),len(fe.variables_1D)+1):
                    f.write(' 1e+36 ')
                f.write("\n")
    f.close()

def writeProfile(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['ASCII']):
        os.makedirs(cfg['global']['ASCII'])
        
    fileName = "{}/{}.{}".format(cfg['global']['ASCII'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    writeHeaderProfile(fileName, cfg, device.lower(), fe, r, )
    print('writing header file: {}'.format(fileName), end='', flush=True)
    print(' done...')
    
    fileName = "{}/{}_{}".format(cfg['global']['ASCII'], 
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
    if not os.path.exists(cfg['global']['ASCII']):
        os.makedirs(cfg['global']['ASCII'])
    
    # write ascii file with human read time and position
    fileName = "{}/{}.{}".format(cfg['global']['ASCII'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing file: {}'.format(fileName), end='', flush=True)
    writeHumanDataTrajectory(fileName, cfg, device.lower(), fe, r, )
    print(' done...')
    
    # write ascii file with decimal time and position
    fileName = "{}/{}_{}".format(cfg['global']['ASCII'], 
        cfg['cruise']['CYCLEMESURE'], device.lower())
    print('writing file: {}'.format(fileName), end='', flush=True)
    writeDecimalDataTrajectory(fileName, cfg, device.lower(), fe, r)
    print(' done...')
   