from jflow.core import datavendor
from base import DataVendor
from datawriter import csvToCache


class csvp(DataVendor):
    
    def __init__(self, h):
        self._h = h
        
    def _history(self, vfid, startdate, enddate):
        ticker = vfid.vid.ticker
        return self._h.rowdata(ticker, startdate, enddate)
            
    def updatehandler(self, vfid, start, end, result):
        csvToCache(vfid,result,self.cache_factory(),self._h.string_to_date)
        return super(csvp,self).updatehandler(vfid, start, end)
    
    def weblink(self, ticker):
        '''
        Provide a link to a web page
        '''
        return self._h.weblink(ticker)


class google(csvp):
    def __init__(self):
        super(google,self).__init__(datavendor.google())
        
class yahoo(csvp):
    def __init__(self):
        super(yahoo,self).__init__(datavendor.yahoo())




google()
yahoo()