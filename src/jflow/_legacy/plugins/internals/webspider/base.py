from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup, SoupStrainer


def trim(v):
    v = str(v).lower().replace(' ','').replace('\n','')
    return v


class scraper(object):
    
    def htmldata(self, url):
        res = urlopen(url)
        html = res.read()
        res.close()
        return html
    
    def filter(self, name, attrs = None):
        attrs = attrs or {}
        return SoupStrainer(name,attrs)
    
    def parser(self, url, filter = None):
        html = self.htmldata(url)
        if filter:
            return BeautifulSoup(html, parseOnlyThese=filter)
        else:
            return BeautifulSoup(html)
