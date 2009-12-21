import calendar
from jflow.core.dates import boostdate


def posixtime(year = 2002, month = 1, day = 1):
    bd = boostdate(year,month,day)
    return bd.timegm() == calendar.timegm((year,month,day,0,0,0))