#!/usr/bin/python
#
# sta-fr22.py
# $Id$

"""
Python script for writing up an station file for SADCP processing CASCADE

usage: 
$ python sta-fr22.py [options] <files>

options are:

  -h, --help		: display this help and quit
  -v, --version		: display program version and quit
  -e, --echo		: display processed file name
  -q, --quiet		: don't display output
  -o, --output=<file>	: write output to file, default is sta-fr22.list

exemple: 
$ python sta-fr22.py ../../CTD/data/FR22*.btl -e
$ python sta-fr22.py ../../CTD/data/FR22*.btl --output=FR22_sta.list
"""

import sys, re, getopt
from datetime import datetime

# initialize variables and options
# --------------------------------
VERSION = "V1.0  J Grelet - IRD - US191 IMAGO, Plouzane - may 2011"
echo  = 0
quiet = 1
outputfile = 'FR22_sta.list'

# initialize datetime object
# --------------------------
dt = datetime

# ---------------------------------------------------------------
# display help using text inside """ """" at the beginning of the
# script with special attribute __doc__ and quit
# ---------------------------------------------------------------
def usage():
  print __doc__
  sys.exit()

# ------------------------------------------------
# display version and quit
# ------------------------------------------------
def version():
  print "%s: %s" % (sys.argv[0], VERSION)
  sys.exit()

# display help with no arg on command-line
# ----------------------------------------
if len(sys.argv) == 1:
  usage()

# setting and get otpions
# -----------------------
try:

  # The return value consists of two elements: the first is a list of 
  # (option, value) pairs; the second is the list of program arguments
  # left after the option list was stripped
  # see optparse, a powerful library for parsing command-line options
  # The gnu version of getopt means that option and non-option
  # arguments may be intermixed
  # ------------------------------------------------------------------
  options, args = getopt.gnu_getopt(sys.argv[1:], 'eqo:hv',
                         ['echo', 'quiet', 'output=', 'help', 'version'])

# if bad option, display an error message and usage
# -------------------------------------------------
except getopt.GetoptError, err:
  print str(err)
  usage()

# iterate over options list
# -------------------------
for option, value in options:
  if option in ('-e', '--echo'):
    echo = 1
  if option in ('-q', '--quiet'):
    quiet = 0
  elif option in ('-o', '--output'):
    outputfile = value
  elif option in ('-h', '--help'):
     usage()
  elif option in ('-v', '--version'):
     version()

# prepare compiled patterns for regular expressions
# extract station number
# -------------------------------------------------
s = re.compile(r"FR22(\d{3})")

# extract CTD station start date 
# ------------------------------
p = re.compile(r"System UpLoad Time\s+=\s+(\w+)\s+(\d+)\s+(\d+)\s+(\d+:\d+:\d+)")

# extract sample date
# -------------------
d = re.compile(r"^\s+\d+\s+(\w+)\s+(\d+)\s+(\d+)\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\(avg\)")

# extract sample time
# -------------------
h = re.compile(r"^\s+(\d+:\d+:\d+)\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\d+.\d+\s+\(sdev\)")

# open output file, need to add some test if open fail
# ----------------------------------------------------
output = open( outputfile, "wr")

# iterate over file list getting with getopt.gnu_getopt 
# ----------------------------------------------------
for arg in args:

  # display processed file name
  # ---------------------------
  if echo: print arg

  # extract station number from file name using compiled regexp s	
  # -------------------------------------------------------------
  if s.search(arg): 
    st = int(s.search(arg).group(1))

  # open current file, add some test  
  # --------------------------------
  file = open( arg, "r")

  # read each line of current file
  # ------------------------------
  for ligne in file.readlines():

    # extract CTD station start date	  
    # ------------------------------
    if  p.search(ligne):
      (month, day, year, hour) = p.search(ligne).groups()	 

    # extract every sample bottle date, and get the last
    # -------------------------------------------------
    if d.search(ligne):
      (e_month, e_day, e_year) =  d.search(ligne).groups()

    # extract every sample bottle time  
    # --------------------------------
    if h.search(ligne):
       e_hour =  h.search(ligne).group(1)	    
  
  # format date and time to  "May 09 2011 16:33:53"
  # -----------------------------------------------
  str1 = "%s/%s/%s %s"  %  (day, month, year, hour)
  str2 = "%s/%s/%s %s"  %  (e_day, e_month, e_year, e_hour)

  # conversion with datetime to "09/05/2011 16:33:53"
  # -------------------------------------------------
  strout = "%2d %s %s" % \
    (st, dt.strptime(str1, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"),  
         dt.strptime(str2, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
 
  # display the converted date and time 
  # -----------------------------------
  if quiet: print strout   

  # print result to file
  # --------------------
  output.write(strout + "\n")  

# display output file name if echo is define
# ------------------------------------------
if echo: print "writing data in %s \n" % (outputfile)    


 
