# tools.py

import math
import re
from datetime import datetime, timedelta

JULIAN = 33282
CNES_EPOCH = datetime(1950, 1, 1)
DEGREE = u"\u00B0"  # u"\N{DEGREE SIGN}"


def dateTime2julian(month, day, year, hour, minute, second):
    # initialize datetime object
    dt = datetime

    # format date and time to  "May 09 2011 16:33:53"
    dateTime = "%s/%s/%s %s:%s:%s" % (day, month, year, hour, minute, second)

    # dateTime conversion to "09/05/2011 16:33:53"
    dateTime = "%s" % (
        dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    )

    # conversion to julian day
    julian = float((dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%j"))) + (
        ((float(hour) * 3600.0) + (float(minute) * 60.0) + float(second)) / 86400.0
    )

    # we use julian day with origine 0
    julian -= 1
    return julian


def dateTime2epic(month, day, year, hour, minute, second):
    # return date as "20110509163353"
    dt = datetime

    dateTime = "%s/%s/%s %s:%s:%s" % (day, month, year, hour, minute, second)

    dateTime = "%s" % (
        dt.strptime(dateTime, "%d/%b/%Y %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    )

    epic_date = "%s" % (
        dt.strptime(dateTime, "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d%H%M%S")
    )

    return epic_date


def julian2dt(jd):
    return CNES_EPOCH + timedelta(days=float(jd))


def julian2format(jd, format="%d/%m/%Y %H:%M:%S"):
    dt = julian2dt(jd)
    return dt.strftime(format)


def dt2julian(dt):
    return (dt - CNES_EPOCH).total_seconds() / 86400.0


# Dec2dmc convert decimal position to degree, mim with centieme string,
# hemi = 0 for latitude, 1 for longitude
def Dec2dmc(position, hemi):
    if re.match("[EW]", hemi):
        neg = "W"
        pos = "E"
    else:
        neg = "S"
        pos = "N"

    if position < 0.0:
        geo = neg
    else:
        geo = pos

    dec, intg = math.modf(position)
    dec = abs(dec)
    intg = abs(intg)

    if re.match("[EW]", hemi):
        str_value = "{:0>3.0f}{:s}{:0>7.4f} {}".format(
            intg, DEGREE, (dec / 100) * 6000, geo
        )
    else:
        str_value = "{:0>2.0f}{:s}{:0>7.4f} {}".format(
            intg, DEGREE, (dec / 100) * 6000, geo
        )

    return str_value


# Dec2dms convert decimal position to degree, mim with second string,
# hemi = 0 for latitude, 1 for longitude
def Dec2dms(position, hemi):
    if re.match("[EW]", hemi):
        neg = "W"
        pos = "E"
    else:
        neg = "S"
        pos = "N"

    if position < 0.0:
        geo = neg
    else:
        geo = pos

    dec, intg = math.modf(position)
    sec, min = math.modf((dec / 100) * 6000)

    if re.match("[EW]", hemi):
        str_value = "{:0>3.0f}{:s}{:2.4f} {}".format(intg, DEGREE, min + sec / 100 * 60, geo)
    else:
        str_value = "{:0>2.0f}{:s}{:2.4f} {}".format(intg, DEGREE, min + sec / 100 * 60, geo)

    return str_value
