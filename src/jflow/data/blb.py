from datetime import date
from itertools import izip

from dynts.data import DataProvider
from bloomberg import BloombergClient


class blb(DataProvider):

    def __init__(self):
        self.server = BloombergClient()
    
    def hasfeed(self, live = False):
        return True
    
    def connect(self):
        self.server.connect()
    
    def connected(self):
        return self.server.connected()
    
    def isconnected(self):
        return self.server.isconnected()
    
    def _history(self, vfid, startdate, enddate):
        '''
        Return a deferred object which wait for an update from the server
        '''
        ticker = vfid.vid.ticker
        field  = vfid.vendor_field.code
        return self.server.history(ticker, startdate, enddate, field)
    
    def registerlive(self, rate):
        return self.server.registerlive(rate)
    
    def updatehandler(self, vfid, start, end, result, hcache):
        if not result:
            return
        
        header = result.get('header')
        body   = result.get('body')
        ticker = header.get('ticker')
        field  = header.get('field')
        tsd    = body.get('timeseries')
        dates  = tsd.get('dates')
        values = tsd.get('values')
        if len(dates) != len(values):
            raise ValueError, "Dates and values of different length"
        
        ts      = hcache.timeseries(vfid)
        for d,v in izip(dates,values):
            try:
                dt = yyyymmdd2date(d)
                ts[dt] = v
            except:
                continue
        return ts
        
    def weblink(self, ticker):
        '''Link to a page on www.bloomberg.com
        '''
        tks = ticker.split(' ')
        N = len(tks)
        typ = tks.pop(N-1)
        if typ == 'Index':
            tks.append('IND')            
        web_ticker = ':'.join(tks)
        return 'http://www.bloomberg.com/apps/quote?ticker=%s' % web_ticker
    
    
register(blb)
    
