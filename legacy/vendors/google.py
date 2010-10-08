from jflow.core import datavendor
from base import DataVendor

class csvp(DataVendor):
    
    def __init__(self, h):
        self._h = h
        
    def _history(self, vfid, startdate, enddate):
        ticker = vfid.vid.ticker
        return self._h.rowdata(ticker, startdate, enddate)
            
    def updatehandler(self, vfid, start, end, result, hcache):
        return csvToCache(vfid,result,self._h.string_to_date,hcache)
        
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



def csvToCache(vfid, data, std, hcache):
    '''
    Write the csv values into cache
    
    @param vfid:
    @param data:
    @param CacheFactory:
    @param std: function string to date converter
    '''  
    if not data:
        return
    vid     = vfid.vid
    field   = vfid.field
    fcode   = vfid.vendor_field.code
    datestr = None
    ts      = hcache.timeseries(vfid)
    
    for r in data:
        try:
            if not datestr:
                val   = None
                dt    = None
                found = 0
                for k,v in r.items():
                    if k == fcode:
                        val    = v
                        found += 1 
                    elif len(k) >= 4:
                        if k[len(k)-4:] == 'Date':
                            datestr = k
                            dt = v
                            found += 1
                    if found == 2:
                        break
                if found < 2:
                    raise ValueError
            else:
                val = r[fcode]
                dt  = r[datestr]
                
            val = float(val)
            dt  = std(dt)
            ts[dt] = val
        except:
            pass
    return ts