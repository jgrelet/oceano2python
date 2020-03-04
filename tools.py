# tools.py

import re
import math
from datetime import datetime
import julian

JULIAN        = 33282
DEGREE        = u"\u00B0"  # u"\N{DEGREE SIGN}"
#DEGREE        = 176

def dateTime2julian(month, day, year, hour, minute, second):
    
    # initialize datetime object
    dt = datetime
        
    # format date and time to  "May 09 2011 16:33:53"
    dateTime = "%s/%s/%s %s:%s:%s" % (
    day, month, year, hour, minute, second)

    # dateTime conversion to "09/05/2011 16:33:53"
    dateTime = "%s" % \
        (dt.strptime(dateTime,
        "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
    
    # conversion to "20110509163353"
    epic_date = "%s" % \
        (dt.strptime(dateTime,
        "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S"))

    # conversion to julian day
    julian = float((dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%j"))) \
           + ((float(hour) * 3600.) +
             (float(minute) * 60.) + float(second)) / 86400.

    # we use julian day with origine 0
    julian -= 1
    return julian

def julian2dt(jd):
    # see: https://en.wikipedia.org/wiki/Julian_day
    # Julian Date	12h Jan 1, 4713 BC
    # Modified JD	0h Nov 17, 1858	JD − 2400000.5
    # CNES JD	0h Jan 1, 1950	JD − 2433282.5
    jd = jd + JULIAN
    dt = julian.from_jd(jd, fmt='mjd')
    return dt

def dt2julian(dt):
    jd = julian.to_jd(dt, fmt='mjd')
    jd = jd - JULIAN
    return jd

def dateTime2epic(month, day, year, hour, minute, second):
    
    # initialize datetime object
    dt = datetime
        
    # format date and time to  "May 09 2011 16:33:53"
    dateTime = "%s/%s/%s %s:%s:%s" % (
    day, month, year, hour, minute, second)

    # dateTime conversion to "09/05/2011 16:33:53"
    dateTime = "%s" % \
        (dt.strptime(dateTime,
        "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S"))
    
    # conversion to "20110509163353"
    epic_date = "%s" % \
        (dt.strptime(dateTime,
        "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S"))

    return  epic_date




# Dec2dmc convert decimal position to degree, mim with centieme string,
# hemi = 0 for latitude, 1 for longitude
def Dec2dmc(position, hemi):

    if re.match('[EW]', hemi):
        neg = 'W'
        pos = 'E'
    else:
        neg = 'S'
        pos = 'N'

    if position < 0:
        geo = neg
    else:
        geo = pos

    # get integer and decimal part
    dec, intg = math.modf(position)
    dec = abs(dec)
    intg = abs(intg)

    if re.match('[EW]', hemi):
        str = "{:0>3.0f}{:s}{:0>7.4f} {}".format(intg, DEGREE, (dec / 100 ) * 6000, geo)
    else:
        str = "{:0>2.0f}{:s}{:0>7.4f} {}".format(intg, DEGREE, (dec / 100 ) * 6000,geo)

    return str

# Dec2dms convert decimal position to degree, mim with second string,
# hemi = 0 for latitude, 1 for longitude
def Dec2dms(position, hemi):

    if re.match('[EW]', hemi):
        neg = 'W'
        pos = 'E'
    else:
        neg = 'S'
        pos = 'N'

    if position < 0:
        geo = neg
    else:
        geo = pos

    # get integer and decimal part
    dec, intg = math.modf(position)
    
    # get integer and decimal part of min.sec
    sec, min = math.modf((dec / 100) * 6000)

    if re.match('[EW]', hemi):
        str = "{:0>3.0f}{:s}{:2.4f} {}".format(intg, DEGREE, min + sec/100*60, geo)
    else:
        str = "{:0>2.0f}{:s}{:2.4f} {}".format(intg, DEGREE, min + sec/100*60, geo)

    return str
