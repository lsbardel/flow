from jflow.db.instdata.models import MktDataCache
from base import DataVendor, DateFromString

short_month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')


class InternetVendor(DataVendor):
    abstract  = True
    separator = '&'
    initquery = '?'
    
    def __init__(self,  url):
        self.baseurl = url
    
    def hystory_url(self, ticker, startdate, enddate):
        raise NotImplementedError

    
    
class InternetVendorCsv(InternetVendor):
    
    def __init__(self, url):
        super(InternetVendorCsv,self).__init__(url)
        
    def get_csv(self, ticker, startdate, enddate):
        from urllib2 import urlopen
        import csv
        url = self.hystory_url(ticker, startdate, enddate)
        try:
            res = urlopen(url)
            return csv.DictReader(res)
        except:
            return None
    
    def string_to_date(self, sdte):
        return DateFromString(sdte)
        
    def _history(self, vfid, startdate, enddate):
        from jflow.core.timeseries import numericts, dateseries
        ticker = vfid.vid.ticker
        result = self.get_csv(str(ticker), startdate, enddate)    
        if not result:
            return
        
        mmo  = MktDataCache.objects
        std  = self.string_to_date
        datestr = None
        for r in result:
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
                m = mmo.get_or_create(vendor_id = vid, field = field, dt = dt)[0]
                m.mkt_value = val
                m.save()
            except:
                pass

    
