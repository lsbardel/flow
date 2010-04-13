
from base import InternetVendorCsv, short_month


class google(InternetVendorCsv):
    
    def __init__(self):
        super(google,self).__init__('http://finance.google.com/finance')
        
    def getdate(self, st, dte):
        m = short_month[dte.month-1]
        return '%s=%s+%s,+%s' % (st,m,dte.day,dte.year)
        
    def hystory_url(self, ticker, startdate, enddate, field = None):
        b = self.baseurl
        st = self.getdate('startdate', startdate)
        et = self.getdate('enddate', enddate)
        return '%s/historical?q=%s&%s&%s&output=csv' % (b,ticker,st,et)
    
    def weblink(self, ticker):
        return '%s?q=%s' % (self.baseurl,ticker)
    
    
    
        