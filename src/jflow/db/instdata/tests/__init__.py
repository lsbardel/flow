

from jflow.db.instdata.id import parsets


def tstest(ts = 'ftse-4*spx', start = None, end = None):
    from datetime import date
    if start == None:
        start = date(2008,1,1)
    if end == None:
        end = date(2008,12,1)
    ts = parsets(ts,start,end)
    a = ts