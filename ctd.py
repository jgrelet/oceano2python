#!/usr/bin/python
#
# ctd.py
# $Id$

"""
Python script for extracting data from SBE-processing files and write out
in various format used by datagui, ODV, Netcdf.

usage: 
$ python3 ctd.py [options] <files>

options are:

  -h, --help		  : display this help and quit
  -v, --version		  : display program version and quit
  -e, --echo		  : display processed file name
  -q, --quiet		  : don't display output
  -o, --output=<file>	  : output file name without extention, default is pirata_fr24
  -r  --roscop=<file>     : load file for code roscop description 
  --cycle_mesure=<name>   : cycle_mesure name
  --plateforme=<name>     : ship or plateforme name
  --date_debut=JJ/MM/YYYY : starting date from cycle_mesure
  --date_fin=JJ/MM/YYYY   : end date from cycle_mesure
  --institut=<name>       : institute name
  --code_oopc=<value>     : processing code
  --pi=<pi_name>          : chief scientist
  --ascii                 : ASCII output instead XML
  --xml                   : XML output (default)
  --odv                   : ODV (Ocean Data View) spreadsheet output	
  --netcdf                : NetCDF OceanSITES output	
  --all                   : ASCII, XML, ODV and NetCDF outputs	
  --local                 : use local DTD for XML
  --secondary             : use T/C secondary sensor
  --sn=<serial_number>
  --type=<instrument_type>   

example: 
$ python3 ctd.py --cycle_mesure=PIRATA-FR29 --institut=IRD --plateforme="THALASSA" --sn=09P01263 --type=SBE911+ --pi=BOURLES --date_debut=01/03/2019 --date_fin=04/04/2019 data/asc/fr29???.hdr --echo --local --ascii
"""

import sys, re, getopt, string, fileinput, csv
from datetime import datetime

# a lire dans la premier fichier
seasave_version = "7.21b"

# initialize constants
VERSION       = "V1.1  J Grelet - IRD - US191 IMAGO, Plouzane - March 2019"
DEGREE        = 176
CODE          = -1
CONTEXTE      = "PIRATA"
TIMEZONE      = "GMT"
FORMAT_DATE   = "DMY"

# initialize variables and options
# --------------------------------
echo          = False
quiet         = True
xml           = True
ascii         = False
odv           = False
netcdf        = False
dtd           = True
debug         = 0
code_oopc     = '0A'
cycle_mesure  = 'PIRATA-FR29'
plateforme    = 'THALASSA'
institut      = 'IRD' 
sn            = '09P01263' 
type          = 'SBE911+' 
pi            = 'BOURLES' 
date_debut    = '01/03/2019'
date_fin      = '04/04/2019'
output_file   = 'pirata-fr29'
latitude      = 0.
latitude_str  = ''
longitude     = 0.
longitude_str = ''
julian        = 0
epic_date     = ''
Pres          = 0
bottom_depth  = 0

# initialize datetime object
# --------------------------
dt = datetime

# ---------------------------------------------------------------
# prepare compiled patterns for regular expressions
# ---------------------------------------------------------------

# extract station number
# -------------------------------------------------
re_station_number = re.compile(r"fr29(\d{3})")

# extract CTD station start date 
# ------------------------------
re_ctd_upload_time = \
  re.compile(r"System UpLoad Time\s*=\s*(\w+)\s+(\d+)\s+(\d+)\s+(\d+):(\d+):(\d+)")

# extract CTD station latitude
# ----------------------------
re_latitude = re.compile(r"NMEA\s+Latitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)")

# extract CTD station longitude
# -----------------------------
re_longitude = re.compile(r"NMEA\s+Longitude\s*[:=]\s*(\d+)\s+(\d+.\d+)\s+(\w)")

# extract bottom depth at station position from echo sounder
# ------------------------------------------------------------
re_bottom_depth = re.compile(r"Bottom\sDepth\s*[:=]\s*(\d+)")

# ---------------------------------------------------------------
# display help using text inside """ """" at the beginning of the
# script with special attribute __doc__ and quit
# ---------------------------------------------------------------
def usage():
  print(__doc__)
  sys.exit()

# ------------------------------------------------
# display version and quit
# ------------------------------------------------
def version():
  print("%s: %s" % (sys.argv[0], VERSION))
  sys.exit()

#------------------------------------------------------------------------------
# entete XML
#------------------------------------------------------------------------------
def entete_xml(fd): 
  #my $today = &dateFormat(undef,"%d/%m/%Y");
  today = '06/03/2019'
  
  fd.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
  # les commentaires ne sont pas acceptes par XML Toolbox Matlab de Geodise
  if (dtd): 
    #fd.write("<!DOCTYPE OCEANO SYSTEM \"M:\ACQUISIT\oceano.dtd\">\n')
    fd.write("<!DOCTYPE OCEANO SYSTEM \"/m/oceano.dtd\">\n")
    #fd.write("<!DOCTYPE OCEANO PUBLIC \"-//US191//DTD OCEANO//FR\" \
    #	      \"http://antea/acquisit/oceano.dtd\">\n')
  else:  
    fd.write("<!DOCTYPE OCEANO PUBLIC \"-//US191//DTD OCEANO//FR\" \
	    \"http://www.brest.ird.fr/us191/database/oceano.dtd\">\n")

  fd.write("<OCEANO TYPE=\"PROFIL\">\n")
  fd.write("  <ENTETE>\n")
  fd.write("    <PLATEFORME>\n")
  fd.write("      <LIBELLE>%s</LIBELLE>\n" % plateforme)  
  fd.write("    </PLATEFORME>\n")
  fd.write("    <CYCLE_MESURE CONTEXTE=\"%s\" TIMEZONE=\"%s\" FORMAT=\"%s\">\n"  % 
               (CONTEXTE, TIMEZONE, FORMAT_DATE))
  fd.write("      <LIBELLE>%s</LIBELLE>\n" % cycle_mesure)  
  fd.write("      <DATE_DEBUT>%s</DATE_DEBUT>\n" % date_debut)  
  fd.write("      <DATE_FIN>%s</DATE_FIN>\n" % date_fin)  
  fd.write("      <INSTITUT>%s</INSTITUT>\n" % institut)  
  fd.write("      <RESPONSABLE>%s</RESPONSABLE>\n" % pi) 
  fd.write("      <ACQUISITION LOGICIEL=\"SEASAVE\" VERSION=\"%s\"></ACQUISITION>\n" %
                  seasave_version) 
  fd.write("      <TRAITEMENT LOGICIEL=\"SBEDATAPROCESSING\" VERSION=\"%s\"></TRAITEMENT>\n" % seasave_version) 
  fd.write("      <VALIDATION LOGICIEL=\"%s\" VERSION=\"%s\" DATE=\"%s\" OPERATEUR=\"%s\" CODIFICATION=\"OOPC\">\n" % (sys.argv[0], VERSION, today, pi))
  fd.write("        <CODE>%s</CODE>\n" % code_oopc)	    
  fd.write("        <COMMENTAIRE>Extraction realisee avant la post-calibration</COMMENTAIRE>\n")
  fd.write("      </VALIDATION>\n")  
  fd.write("    </CYCLE_MESURE>\n")  
  fd.write("    <INSTRUMENT TYPE=\"%s\" NUMERO_SERIE=\"%s\">\n" % (type, sn)) 
  fd.write("    </INSTRUMENT>\n")  
  
  #decode_con_file(fileName)
  
  fd.write("  </ENTETE>\n")  
  fd.write("  <DATA>\n")  

#------------------------------------------------------------------------------
# read code roscop file
#------------------------------------------------------------------------------
def codeRoscop(file):
  print("Code roscop file: %s" % code_roscop)
  with open(code_roscop, 'rt') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        print("%s : %s : %s : %s : %s" % (row['key'],  row['long_name'], 
        row['standard_name'], row['units'], row['format']))
  sys.exit()

# display help with no arg on command-line
# ----------------------------------------
if len(sys.argv) == 1:
  usage()

# setting and get otpions
# -----------------------
try:

  # The return args consists of two elements: the first is a list of 
  # (option, arg) pairs; the second is the list of program arguments
  # left after the option list was stripped
  # see optparse, a powerful library for parsing command-line options
  # The gnu version of getopt means that option and non-option
  # arguments may be intermixed
  # The -e is a simple flag, while -d, -o and -r require an argument. 
  # The option definition string is "ed:r:".
  # To mix option and non-option arguments on the command line in any order, 
  # use gnu_getopt() instead getopt
  # ------------------------------------------------------------------
  options, args = getopt.gnu_getopt(sys.argv[1:], 'ed:qo:hvr:',
      ['echo', 'debug=', 'quiet', 'output=', 'help', 'version', 'roscop=',
       'cycle_mesure=', 'plateforme=', 'date_debut=', 'date_fin=',
       'institut=', 'code_oopc=', 'pi=', 'ascii', 'xml', 'odv', 
       'netcdf', 'all', 'local', 'secondary', 'sn=', 'type='])

# if bad option, display an error message and usage
# -------------------------------------------------
except getopt.GetoptError as err:
  print(str(err))
  usage()

# iterate over options list
# -------------------------
for option, arg in options:
  if option in ('-e', '--echo'):
    echo = True
  elif option in ('-q', '--quiet'):
    quiet = False
  elif option in ('-d', '--debug'):
    debug = int(arg)
  elif option in ('-o', '--output'):
    outputfile = arg
  elif option in ('-h', '--help'):
    usage()
  elif option in ('-v', '--version'):
    version()
  elif option in ('-r', '--roscop'):
    code_roscop = arg
    codeRoscop(code_roscop)
  elif option == '--cycle_mesure':
    cycle_mesure = arg
  elif option == '--plateforme':
    plateforme = arg
  elif option == '--date_debut':
    date_debut = arg
  elif option == '--date_fin':
    date_fin = arg
  elif option == '--institut':
    institut = arg
  elif option == '--code_oopc':
    code_oopc = arg
  elif option == '--pi':
    pi = arg
  elif option == '--ascii':
    ascii = True
  elif option == '--xml':
    xml = True
  elif option == '--odv':
    odv = True
  elif option == '--netcdf':
    netcdf = True
  elif option == '--all':
    ascii = xml = odv = netcdf = True

# for debug only, display arg list
# --------------------------------
if debug == 1:
  print("Args: %s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
    (cycle_mesure, plateforme, date_debut, date_fin, institut,
     code_oopc, pi))

# open ascii files
# ----------------
if ascii: 
  hdr_file   = open( output_file + '.ctd', "w")
  ascii_file = open( output_file + '_ctd', "w")

  # write header to ascii files
  # ---------------------------------
  hdr_file.write("//%s  %s  %s  %s  %s  %s\n" % \
      (cycle_mesure, plateforme, institut, type, sn, pi))
  hdr_file.write("St    Date      Time    Latitude  Longitude  Depth\n")
  ascii_file.write("//%s  %s  %s  %s  %s  %s\n" % \
      (cycle_mesure, plateforme, institut, type, sn, pi))
  ascii_file.write("PRFL  PRES  TEMP    PSAL    DENS     SVEL     DOX2    FLU2    TUR3    NAVG\n")

# open xml file
# -------------
if xml:
  xml_file = open( output_file + '_ctd.xml', "w")

  # write header to xml files
  # ---------------------------------
  entete_xml(xml_file)
  xml_file.write("PRFL  PRES  TEMP    PSAL    DENS     SVEL     DOX2    FLU2    TUR3    NAVG\n")

if echo: 
  # display selected output format
  # ------------------------------
  print("Output: ")
  if (ascii): print("ASCII ")
  if (xml)  : print("XML ")
  if (odv)  : print("ODV ")

  # display header
  # --------------
  print("\n//%s  %s  %s  %s  %s  %s" % \
      (cycle_mesure, plateforme, institut, type, sn, pi))
  print("   File              St    Date      Time    Latitude  Longitude    Depth Bottom", end='')

# iterate over file list getting with getopt.gnu_getopt 
# ----------------------------------------------------
for fileName in args:

  # display processed filename
  # suppress '\n' character written at the end with a comma
  # -------------------------------------------------------
  if echo: print("\n%s" % (fileName), end='')

  # extract station number from file name using compiled regexp	
  # -----------------------------------------------------------
  if re_station_number.search(fileName): 
    station = int(re_station_number.search(fileName).group(1))

  # open current file
  # TODOS: add some tests on file existence  
  # ---------------------------------------
  file = open( fileName, "r", encoding = "ISO-8859-1")

  # read each line of current file
  # ------------------------------
  for line in file.readlines():

    # extract CTD station start date	  
    # ------------------------------
    if re_ctd_upload_time.search(line):
      (month, day, year, hour, minute, second) = \
	  re_ctd_upload_time.search(line).groups()	 

      # format date and time to  "May 09 2011 16:33:53"
      # -----------------------------------------------
      dateTime = "%s/%s/%s %s:%s:%s"  %  (day, month, year, hour, minute, second)

      # dateTime conversion to "09/05/2011 16:33:53"
      # --------------------------------------------
      dateTime = "%s" % \
        (dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))  
      # conversion to "20110509163353"
      # --------------------------------------------
      epic_date = "%s" % \
        (dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S"))  

      # conversion to julian day
      # ------------------------
      julian = float((dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%j"))) \
	  + ((float(hour) * 3600.) + (float(minute) * 60.) + float(second) ) / 86400.

      # we use julian day with origine 0
      # --------------------------------
      julian -= 1

    # extract latitude conversion 
    # --------------------------------------------
    if re_latitude.search(line):
      (lat_deg, lat_min, lat_hemi) = re_latitude.search(line).groups() 

      # format latitude to string
      # -------------------------
      latitude_str = "%s%c%s %s" % (lat_deg, DEGREE, lat_min, lat_hemi)

      # transform to decimal using ternary operator
      # -------------------------------------------
      latitude = float(lat_deg) + (float(lat_min) / 60.) if lat_hemi == 'N' else \
        (float(lat_deg) + (float(lat_min) / 60.)) * -1

    # extract longitude conversion 
    # --------------------------------------------
    if re_longitude.search(line):
      (lon_deg, lon_min, lon_hemi) = re_longitude.search(line).groups() 

      # format longitude to string
      # -------------------------
      longitude_str = "%s%c%s %s" % (lon_deg, DEGREE, lon_min, lon_hemi)

      # transform to decimal using ternary operator
      # -------------------------------------------
      longitude = float(lon_deg) + (float(lon_min) / 60.) if lon_hemi == 'E' \
	  else (float(lon_deg) + (float(lon_min) / 60.)) * -1

    # extract bottom depth 
    # --------------------------------------------
    if re_bottom_depth.search(line):
      bottom_depth = re_bottom_depth.search(line).group(1) 

  # close header file
  # -----------------
  file.close()

  # display header information in console
  # -------------------------------------
  if echo: print(" %03d %s %s %s %5.0f %5.0f" % \
    (station, dateTime, latitude_str, longitude_str, float(Pres), 
    float(bottom_depth)), end = '')

  # write station header to ascii files
  # -----------------------------------
  if ascii:
    hdr_file.write("%03d %s %s %s %5.0f\n" % \
    (station, dateTime, latitude_str, longitude_str, float(Pres)))

    # write station header in decimal with PRES = -1, and 5 decimals
    # --------------------------------------------------------------
    ascii_file.write("%3d  %4d %9.5f %8.5f %9.5f %s 1e36 1e36 1e36 1e36\n" % \
	(station, CODE, julian, latitude, longitude, epic_date))

    # write station header in decimal with PRES = -1, and 5 decimals
    # --------------------------------------------------------------
    xml_file.write("%3d  %4d %9.5f %8.5f %9.5f %s 1e36 1e36 1e36 1e36\n" % \
	(station, CODE, julian, latitude, longitude, epic_date))

  # substitute .hdr or .HDR in fileName with .asc
  # ---------------------------------------------
  fileName = re.sub(r'\.(?i)hdr$', '.asc', fileName)

  # we don't use __builtin__ readline method of file object that haven't
  # method to get read line number  
  # --------------------------------------------------------------------
  file = fileinput.input(fileName, openhook=fileinput.hook_encoded("ISO-8859-1"))

  # iterate over the lines of opened file "fileName"
  # ------------------------------------------------
  for line in file:

    # skip header line
    # ----------------
    if file.isfirstline(): 
      continue
    else:

      # extract data
      # ------------
      (scan,TimeJ,Pres,Depth,T0,T1,C0,C1,v1,v2,v1dt,v2dt,Xmiss,FlC,Aqua,Ox0,Ox1,S0,S1,sigmateta0, \
	  sigmateta1,sndvel0,sndvel1,nbin,flag) = line.split()

      # write data to ascii file
      # ------------------------
      if ascii:
        ascii_file.write( \
	   "%3d  %4d  %6.5g  %6.5g  %6.3f  %7.2f  %7.6g  %6.4g  %7.6g  %3d\n" % \
	   (station, float(Pres), float(T0), float(S0), float(sigmateta0), \
	   float(sndvel0), float(Ox0), float(FlC), float(Xmiss), int(nbin)))

      # write data to xml file
      # ------------------------
      if xml:
        xml_file.write( \
	   "%3d  %4d  %6.5g  %6.5g  %6.3f  %7.2f  %7.6g  %6.4g  %7.6g  %3d\n" % \
	   (station, float(Pres), float(T0), float(S0), float(sigmateta0), \
	   float(sndvel0), float(Ox0), float(FlC), float(Xmiss), int(nbin)))
  

  # close current file
  # ------------------
  file.close()

# end of loop over files
# ----------------------
if echo:
  print("\n")

# close files
# -----------
if ascii: 
  hdr_file.close()
  ascii_file.close()
    
if xml:
  xml_file.write("  </DATA>\n")  
  xml_file.write("</OCEANO>\n")  
  xml_file.close()
