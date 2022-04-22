# ascii.py
# write hdr and data in ascii files

import os
import tools
import numpy as np
from datetime import datetime
    
def writeHeader(hdrFile, cfg, device, fe, r):
    f = open(hdrFile, 'w')
    # first line, header ex: 
    # PIRATA-FR30  THALASSA  IRD  SBE911+  09P-1263  BOURLES
    print("{}  {}  {}  {}  {}  {}".format(cfg['cruise']['cycleMesure'], 
        cfg['cruise']['plateforme'], cfg['cruise']['institute'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['pi']))
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['cycleMesure'], 
        cfg['cruise']['plateforme'], cfg['cruise']['institute'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['pi']))
    # write next lines, start and end profile ex: 
    # 00001 18/02/2020 19:04:19 18/02/2020 22:41:07 11°28.85 N 023°00.59 W  4063  5083 fr30001
    # add PROFILE and END_PROFILE_TIME, BATH
    for i in range(fe.n):
        for k in fe.variables_1D:
            if k == 'TIME':
                t = tools.julian2dt(fe['TIME'][i]).strftime("%d/%m/%Y %H:%M:%S")
                print(f"{t}  ", end='')
                f.write(f"{t}  ")
                #query = self.db.query('SELECT end_date_time FROM station')
                # need to cast <class 'numpy.int32'> to int 
                query = fe.db.select('station', ['end_date_time'], station = int(fe['PROFILE'][i]))
                for idx, item in enumerate(query):
                    dt = item['end_date_time']
                    if dt == None:
                        pass
                    else:
                        print(f"{dt}  ", end='')
                        f.write(f"{dt}  ")

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
                if np.isnan(fe[k][i]):
                    #print(k, type(fe[k][i]))
                    print(' 1e+36 ', end='')
                    f.write(' 1e+36 ')
                else:
                    print(f"{fmt}  " % (fe[k][i]), end='')
                    f.write(f"{fmt}  " % (fe[k][i]))

        # get max value for each profile
        col = f"MAX({fe.keys[0]})"
        query = fe.db.query(
            f"SELECT {col} FROM data WHERE station_id = {int(fe['PROFILE'][i])}")
        for idx, item in enumerate(query):
            dt = item[col]
            if dt == None:
                pass
            else:
                print("%6.1f  " % (item[col]), end='')
                f.write("%6.1f  " % (item[col]))
        print(end = '\n')
        f.write('\n')
      
    f.close()
    
    
def writeData(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    # write header, first line
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['cycleMesure'], 
        cfg['cruise']['plateforme'], cfg['cruise']['institute'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['pi']))

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
                f.write(f" {fmt} {'%s'}" % (fe[k][i] - fe.julian_from_year, 
                    tools.julian2dt(fe[k][i]).strftime("%Y%m%d%H%M%S")))
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

def writeAscii(cfg, device, fe, r):
    if not os.path.exists(cfg['global']['ascii']):
        os.makedirs(cfg['global']['ascii'])
        
    fileName = "{}/{}.{}".format(cfg['global']['ascii'], 
        cfg['cruise']['cycleMesure'], device.lower())
    print('writing header file: {}'.format(fileName))
    writeHeader(fileName, cfg, device.lower(), fe, r, )
    
    fileName = "{}/{}_{}".format(cfg['global']['ascii'], 
        cfg['cruise']['cycleMesure'], device.lower())
    print('writing  data  file: {}'.format(fileName), end='', flush=True)
    writeData(fileName, cfg, device.lower(), fe, r)
    print(' done...')
   