from datetime import date, datetime, timedelta
from jflow.lib import boostdate, juldate, TradingCentres
    
now = datetime.now
today = date.today

short_month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')


def prevbizday(dte = None, nd = 1):
    tcs = TradingCentres()
    dte = dte or today()
    return tcs.prevbizday(dte,nd)

def nextbizday(dte = None, nd = 1):
    tcs = TradingCentres()
    dte = dte or today()
    return tcs.nextbizday(dte,nd)

def date_prevbizday(dte = None, nd = 1):
    dt = prevbizday(dte,nd)
    return date(dt.year,dt.month,dt.day)

def date_nextbizday(dte = None, nd = 1):
    dt = nextbizday(dte,nd)
    return date(dt.year,dt.month,dt.day)
