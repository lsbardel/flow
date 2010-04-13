
from base import *
import bloomberg


class blb(DataVendor):

    def __init__(self):
        self.server = bloomberg.BloombergClient()
    
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
    
    def historyarrived(self, fvid, res):
        if res == None:
            return
        
        header = res.get('header')
        body   = res.get('body')
        ticker = header.get('ticker')
        field  = header.get('field')
        ts     = body.get('timeseries')
        dates  = ts.get('dates')
        values = ts.get('values')
        if len(dates) != len(values):
            raise ValueError, "Dates and values of different length"
        
        vid    = fvid.vid
        field  = fvid.field
        vi     = values.__iter__()
        mmo    = self.cache_factory()
        for d in dates:
            v = vi.next()
            m = mmo.get_or_create(vendor_id = vid, field = field, dt = DateFromString(d))[0]
            m.mkt_value = v
            m.save()
            
    def weblink(self, ticker):
        '''
        link to a page on www.bloomberg.com
        '''
        tks = ticker.split(' ')
        N = len(tks)
        typ = tks.pop(N-1)
        if typ == 'Index':
            tks.append('IND')            
        web_ticker = ':'.join(tks)
        return 'http://www.bloomberg.com/apps/quote?ticker=%s' % web_ticker
    
blb().connect()
    
