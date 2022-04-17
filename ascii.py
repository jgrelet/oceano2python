# ascii.py
# write hdr and data in ascii files

import os
import tools
    
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
        print("{:0>5d}  {}  {}  {}  {}".format(fe['PROFILE'][i], 
            tools.julian2dt(fe['TIME'][i]).strftime("%d/%m/%Y %H:%M:%S"), 
            tools.Dec2dmc(fe['LATITUDE'][i],'N'), tools.Dec2dmc(fe['LONGITUDE'][i],'W'),
            fe['BATH'][i]))
        f.write("{:0>5d}  {}  {}  {}  {}\n".format(fe['PROFILE'][i], 
            tools.julian2dt(fe['TIME'][i]).strftime("%d/%m/%Y %H:%M:%S"), 
            tools.Dec2dmc(fe['LATITUDE'][i],'N'), tools.Dec2dmc(fe['LONGITUDE'][i],'W'),
            fe['BATH'][i]))
    f.close()
    
    
def writeData(dataFile, cfg, device, fe, r):
    f = open(dataFile, 'w')

    f.write("{}  {}  {}  {}  {}  {}\n".format(cfg['cruise']['cycleMesure'], 
        cfg['cruise']['plateforme'], cfg['cruise']['institute'],
        cfg[device]['typeInstrument'], cfg[device]['instrumentNumber'],
        cfg['cruise']['pi']))

    for i in range(fe.n):
        f.write("{:0>5d}  {:>-5}  {:>8.2}  {:>2.5}  {:>3.5}  {} {:>4.1}\n".format(fe['PROFILE'][i], 
            -1, fe['TIME'][i], fe['LATITUDE'][i], fe['LONGITUDE'][i],
            tools.julian2dt(fe['TIME'][i]).strftime("%Y%m%d%H%M%S"), fe['BATH'][i]))
        for m in range(fe.m):
            #print(fe['PRES'])
            if fe['PRES'][i][m] < 1e35:
                f.write("{:0>5} ".format(fe['PROFILE'][i]))
                for k in fe.keys:        
                    f.write("{:0>5.2f} ".format( fe[k][i][m]))
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
    print('writing  data  file: {}'.format(fileName), end='')
    writeData(fileName, cfg, device.lower(), fe, r)
    print(' done...')
   