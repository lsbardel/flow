
from base import InternetVendorCsv


class yahoo(InternetVendorCsv):
    
    def __init__(self):
        super(yahoo,self).__init__('http://ichart.yahoo.com')
        
    def getdate(self, st, dte):
        return '%s=%s&%s=%s&%s=%s' % (st[0],dte.month-1,st[1],dte.day,st[2],dte.year)
        
    def hystory_url(self, ticker, startdate, enddate):
        b = self.baseurl
        st = self.getdate(('a','b','c'), startdate)
        et = self.getdate(('d','e','f'), enddate)
        return '%s/table.csv?s=%s&%s&%s&g=d&ignore=.csv' % (b,ticker,st,et)
    
    def weblink(self, ticker):
        return 'http://finance.yahoo.com/q?s=%s' % ticker