import csv
from urllib import urlopen
from datetime import timedelta

from dateutil.parser import parse as DateFromString

#from jflow.core.dates import DateFromString, get_date
#from jflow.lib import numericts, numerictsv, dateseries


short_month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')


class DataVendor(object):
    '''
    Interface class for Data Vendors
    '''    
    def __repr__(self):
        return self.code + ' financial data provider'
    
    def __get_code(self):
        return self.__class__.__name__
    code = property(fget = __get_code)
    
    def weblink(self, ticker):
        '''
        Provide a link to a web page
        '''
        return None
    
    def external(self):
        return True
    
    def hasfeed(self, live = False):
        return not live
    
    def connect(self):
        pass
        
    def isconnected(self):
        '''
        Return True if data vendor connection is available
        '''
        return True
    
    def _get(self, ticker, startdate, enddate, field):
        '''
        this function should be implemeneted by derived classes.
        By default do nothing, which is fine
        '''
        raise NotImplementedError
    
    def get(self, ticker, startdate, enddate, field = None):
        '''
        this function should be implemeneted by derived classes.
        By default do nothing, which is fine
        '''
        return self._get(ticker,get_date(startdate),get_date(enddate),field)
    
    
    
class InternetVendor(DataVendor):
    separator = '&'
    initquery = '?'
    
    def __init__(self,  url):
        self.baseurl = url
    
    def hystory_url(self, ticker, startdate, enddate):
        raise NotImplementedError
    
    
    
class InternetVendorCsv(InternetVendor):
    
    def __init__(self, url):
        super(InternetVendorCsv,self).__init__(url)
    
    def string_to_date(self, sdte):
        return DateFromString(sdte)
    
    def rowdata(self, ticker, startdate, enddate, field = None):
        url = self.hystory_url(str(ticker), startdate, enddate)
        try:
            res = urlopen(url)
            return csv.DictReader(res)
        except Exception, e:
            return None
        
    def _get(self, ticker, startdate, enddate, field = None):
        data = self.rowdata(ticker, startdate, enddate)
        if not data:
            return
        
        fields = {}        
        std  = self.string_to_date
        datestr = None
        for r in data:
            try:
                if not datestr:
                    val   = None
                    dt    = None
                    found = 0
                    for k,v in r.items():
                        if len(k) >= 4:
                            if k[len(k)-4:] == 'Date':
                                datestr = k
                                continue
                        ts = numericts()
                        fields[str(k).upper()] = ts
                dt  = std(r[datestr])
                for k,v in r.items():
                    nts = fields.get(str(k).upper(),None)
                    if nts is not None:
                        try:
                            nts[dt] = float(v)
                        except:
                            continue
            except:
                continue
        
        if field:
            return fields.get(str(field).upper(),None)
        else:
            ts = numerictsv()
            for k,v in fields.items():
                ts.addts(v);
            return ts
    
        