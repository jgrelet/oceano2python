# ascii.py
# write hdr and data in ascii files

import os
import tools

def writeAscii(cfg, device, fe, r, variables_1D):
    if not os.path.exists(cfg['global']['ascii']):
        os.makedirs(cfg['global']['ascii'])
        
    fileName = "{}/{}.{}".format(cfg['global']['ascii'], cfg['cruise']['cycleMesure'], device.lower())
    print('writing header file: {}'.format(fileName))
    writeHeader(fileName, cfg, fe, r, variables_1D, device.lower())
    
    fileName = "{}/{}_{}".format(cfg['global']['ascii'], cfg['cruise']['cycleMesure'], device.lower())
    print('writing  data  file: {}'.format(fileName), end='')
    writeData(fileName, cfg, fe, r, variables_1D)
    print(' done...')
    
def writeHeader(hdrFile, cfg, fe, r, variables_1D, device):
    f = open(hdrFile, 'w')
    # first line, header ex: 
    # PIRATA-FR30  THALASSA  IRD  SBE911+  09P-1263  BOURLES
    print("{}  {}  {}  {}  {}  {}".format(cfg['cruise']['cycleMesure'], cfg['cruise']['plateforme'], cfg['cruise']['institute'],
                                cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
                                cfg['cruise']['pi']))
    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['cycleMesure'], cfg['cruise']['plateforme'], cfg['cruise']['institute'],
                                cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
                                cfg['cruise']['pi']))
    # write next lines, start and end profile ex: 
    # 00001 18/02/2020 19:04:19 18/02/2020 22:41:07 11°28.85 N 023°00.59 W  4063  5083 fr30001
    # add PROFILE and END_PROFILE_TIME, BATH
    for i in range(fe.n):
        print("{:0>5d}  {}  {}  {}  {}".format(i+1, tools.julian2dt(fe['TIME'][i]).strftime("%d/%m/%Y %H:%M:%S"), 
              tools.Dec2dmc(fe['LATITUDE'][i],'N'), tools.Dec2dmc(fe['LONGITUDE'][i],'W'), fe['BATH'][i]))
        f.write("{:0>5d}  {}  {}  {}  {}\n".format(i+1, tools.julian2dt(fe['TIME'][i]).strftime("%d/%m/%Y %H:%M:%S"), 
              tools.Dec2dmc(fe['LATITUDE'][i],'N'), tools.Dec2dmc(fe['LONGITUDE'][i],'W'), fe['BATH'][i]))
    f.close()
    
    
def writeData(dataFile, cfg, fe, r, variables_1D):
    f = open(dataFile, 'w')
    f.write("ASCII file OK !")
    f.close()
   