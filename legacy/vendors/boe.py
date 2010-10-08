
'http://www.bankofengland.co.uk/mfsd/iadb/fromshowcolumns.asp?Travel=NIxIRxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Jan&FY=1963&TD=24&TM=Feb&TY=2009&VFD=N&html.x=19&html.y=19&CSVF=TT&C=EC3&Filter=N'
'http://www.bankofengland.co.uk/mfsd/iadb/fromshowcolumns.asp?Travel=NIxIRxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Jan&FY=1963&TD=24&TM=Feb&TY=2009&VFD=N&html.x=15&html.y=20&CSVF=TT&C=EC8&Filter=N'

_months = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')


def fromtodates(fd, td):
    a = 'FD=%s&FM=%s&FY=%s' % (fd.day,_months[fd.month-1],fd.year)
    b = 'TD=%s&TM=%s&TY=%s' % (td.day,_months[td.month-1],td.year)
    return '%s&%s' % (a,b)


_ccys = {'AUD':'html.x=15&html.y=20',
         'CAD':'html.x=16&html.y=22',
         'EUR':'VFD=N&html.x=29&html.y=12&CSVF=TT&C=C8J&Filter=N',
         'USD':''
         }

base_url = 'http://www.bankofengland.co.uk/mfsd/iadb/fromshowcolumns.asp?Travel=NIxIRxSUx&FromSeries=1&ToSeries=50&DAT=RNG&'

def spotrateurl(ccy,fd,td):
    dt = fromtodates(fd,td)
    url = _ccys.get(ccy,None)
    if url:
        return '%s&%s&s' % (base_url,dt,url)
    else:
        return None
    


class boe():
    base_url = 'http://www.bankofengland.co.uk/mfsd/iadb/fromshowcolumns.asp?Travel=NIxIRxSUx&FromSeries=1&ToSeries=50&DAT=RNG&'
    
    def getdate(self, c, dte):
        return '%s=%s&%s=%s&%s=%s' % (st[0],dte.month,st[1],dte.day,st[2],dte.year)
    
    def from_date(self, dte):
        return 

    