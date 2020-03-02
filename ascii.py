# ascii.py
# write hdr and data in ascii files

import os

def writeAscii(cfg, device, fe, r, variables_1D):
    if not os.path.exists(cfg['global']['ascii']):
        os.makedirs(cfg['global']['ascii'])
        
    fileName = "{}/{}.{}".format(cfg['global']['ascii'], cfg['cruise']['cycleMesure'], device.lower())
    print('writing header file: {}'.format(fileName))
    writeHeader(fileName, fe, r, variables_1D)
    
    fileName = "{}/{}_{}".format(cfg['global']['ascii'], cfg['cruise']['cycleMesure'], device.lower())
    print('writing Ascii data file: {}'.format(fileName))
    writeData(fileName, fe, r, variables_1D)
    print('done...')
    
def writeHeader(hdrFile, fe, r, variables_1D):
    f = open(hdrFile, 'w')
    f.write("Header file OK !")
    f.close()
    
    
def writeData(dataFile, fe, r, variables_1D):
    f = open(dataFile, 'w')
    f.write("ASCII file OK !")
    f.close()
   