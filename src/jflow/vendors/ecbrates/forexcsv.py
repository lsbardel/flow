import os
import csv
from urllib2 import urlopen
import zipfile

from jflow.core.dates import DateFromString
from jflow.db import geo

from base import url_base

url_last = '/stats/eurofxref/eurofxref.zip?7868c3636657e87c3ca4aa749c1eaf9c'

def urlcsvzip(url):
    '''
    Read a csv zipped file from a url
    '''
    res = urlopen(url)
    data = os.tmpfile()
    data.write(res.read())
    archive = zipfile.ZipFile(data,"r")
    if archive.testzip() != None:
        raise ValueError, 'Invalid zip file at %s' % url
    contents = archive.namelist()
    if len(contents) == 1:
        item    = contents[0]
        csvdata = archive.read(item)
        return csv.DictReader(csvdata.split('\n'))
    else:
        return None

def load_last():
    url = '%s%s' % (url_base,url_last)
    res = urlcsvzip(url)
    if res:
        for ccys in res:
            dt  = DateFromString(ccys.pop('Date')).date()
            # Get the EURUSD rate
            eur = float(ccys.pop(' USD'))
            for c,v in ccys.items():
                c  = c.replace(' ','')
                cc = geo.currency(c)
                v  = float(v)
                
            print r
    
    
if __name__ == '__main__':
    r = load_last()
    print r
    
    