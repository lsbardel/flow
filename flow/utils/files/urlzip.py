import os
from urllib2 import urlopen
import zipfile

__all__ = ['urlzip']

def urlzip(url):
    '''
    Read a zip file from a url
    '''
    res = urlopen(url)
    data = os.tmpfile()
    data.write(res.read()) 
    archive = zipfile.ZipFile(data,"r")
    if archive.testzip() != None:
        raise ValueError, 'Invalid zip file at %s' % url
    contents = archive.namelist()
    for item in contents:
        print item