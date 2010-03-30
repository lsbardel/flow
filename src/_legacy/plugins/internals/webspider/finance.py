from base import scraper, trim

class companyinfo(object):
    
    def __init__(self, name = ''):
        self.vendors     = {}
        self.data        = {'vendors': self.vendors,
                            'name': name}
        
    def __getattr__(self, name):
        return self.data.get('data',None)
        
    def add(self, name, ticker):
        self.vendors[name] = ticker
    
    def __str__(self):
        return self.data.get('name',None)
    
    
class finance(scraper):
    baseurls = []
    defextra = ''
    symbol   = ''
    
    def weburl(self, ticker, extra = None):
        extra = extra or self.defextra
        return '%s%s?%s=%s' % (self.baseurls[0],extra,self.symbol,ticker)
    
    def checkurl(self, url):
        '''
        check if a valid url and return the ticker
        '''
        s = url.split('?')
        if len(s) == 2:
            for burl in self.baseurls:
                N = len(burl)
                if len(url) > N:
                    if url[:N] == burl:
                        data = self.params(s[1])
                        return data.get(self.symbol,None)
        return None
    
    def params(self, st):
        data = {}
        sts = st.split('&')
        for s in sts:
            k,v = s.split('=')
            data[k] = v
        return data
    
    
    
class reuters(finance):
    baseurls = ['http://www.reuters.com/finance/stocks/',
                'http://stocks.us.reuters.com/stocks/']
    symbol   = 'symbol'
    defextra = 'companyProfile'
    
    def companyprofile(self, ticker):
        url  = self.weburl(ticker)
        parser = self.parser(url, self.filter('div', {'class': 'primaryContent'}))
        links  = parser.find('div', {'class': 'label'}).findAll('a')
        try:
            sector   = str(links[0].contents[0])
        except:
            sector = None
        try:
            industry = str(links[1].contents[0])
        except:
            industry = None
        try:
            desdiv      = parser.find('div', {'class': 'module'})
            pdesdiv     = desdiv.findAll('p')
            if pdesdiv:
                description = str(pdesdiv[0].contents[0])
            else:
                description = str(desdiv.contents[0])
        except:
            description = None
        return (sector,industry,description)


class google(finance):
    baseurls = ['http://www.google.co.uk/finance']
    symbol   = 'q'
    
    def getinfo(self, ticker):
        url    = self.weburl(ticker)
        # Get the main document
        #parser = self.parser(url, self.filter('div', {'class': 'dbody'}))
        # Modified Aug 2009
        parser = self.parser(url, self.filter('div', {'id': 'rt-content'}))
        self.parser = parser
        
        # Get the company name
        res    = parser.find('div',{'id': 'companyheader'})
        if res:
            name = str(res.find('h3').contents[0])
            ci   = companyinfo(name = name)
            ci.add('google',ticker)
            return ci
    
    
        

class yahoo(finance):
    baseurls = ['http://finance.yahoo.com/q',
                'http://uk.finance.yahoo.com/q']
    symbol   = 's'    
    
class bloomberg(finance):
    baseurls = ['http://www.bloomberg.com/apps/quote']
    symbol   = 'ticker'
    
    def weburl(self, ticker, extra = None):
        tks = ticker.split(' ')
        N = len(tks)
        typ = tks.pop(N-1)
        if typ == 'Index':
            tks.append('IND')            
        web_ticker = ':'.join(tks)
        return super(bloomberg,self).weburl(web_ticker,extra)
    
    def companyprofile(self, ticker):
        '''
        Check company profile from Bloomber Personal Finance
        '''
        url = self.weburl(ticker)
        parser = self.parser(url, self.filter('div', {'class': 'QuoteTableData'}))
        for p in parser:
            c = str(p.contents[0])
            if len(c) > 40:
                return c
            
