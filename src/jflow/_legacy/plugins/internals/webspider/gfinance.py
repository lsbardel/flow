
import finance

class exchvalue(object):
    '''
    Store information about the geographical and exchange
    of a ticker
    '''
    def __init__(self, exchange, country, blb, multiplier, sd):
        self.exchange = exchange
        self.country  = country
        self.blb      = blb
        self.multiplier = multiplier
        self.settlement_delay = sd
        
    def __str__(self):
        return '%s default country %s, bloomberg mid code %s' % (self.exchange,self.country,self.blb)
        

exchanges = {'LON': exchvalue('LSE','UK','LN',0.01,2),
             'NYSE': exchvalue('NYSE','US','US',1,2),
             'NASDAQ': exchvalue('NASDAQ','US','US',1,2),
             }
        

def gfinance(ticker):
    # initialize web-scrapers
    goo    = finance.google()
    reu    = finance.reuters()
    yah    = finance.yahoo()
    blb    = finance.bloomberg()
    
    parts  = ticker.split(':')
    exch   = parts[0].upper()
    secu   = parts[1].upper()
    exch   = exchanges.get(exch,None)
    
    # Start from google
    ci     = goo.getinfo(ticker)
    if not ci:
        return
        
    cta = ci.data
    if exch:
        cta['exchange']         = exch.exchange
        cta['country']          = exch.country
        cta['multiplier']       = exch.multiplier
        cta['settlement_delay'] = exch.settlement_delay
        
    links = goo.parser.findAll('a')
        
    for l in links:
        href = l.get('href')
        if href and href.startswith('http'):
            if not ci.vendors.get('reuters',None):
                tick = reu.checkurl(href)
                if tick:
                    ci.add('reuters',tick)
                    cta['datasector'], cta['industry'], cta['description'] = reu.companyprofile(tick)
            if not ci.vendors.get('yahoo',None):
                tick = yah.checkurl(href)
                if tick:
                    ci.add('yahoo',tick)
        
    # Try bloomberg
    if exch:
        btik = '%s %s Equity' % (secu,exch.blb)
        cta['code'] = '%s_%s' % (secu,exch.blb)
    else:
        btik = '%s Index' % secu
        cta['code'] = secu
        
    des = blb.companyprofile(btik)
    if des:
        ci.add('blb',btik)
        if not cta.get('description',None):
            cta['description'] = des
                
    return ci
        

if __name__ == '__main__':
    test = gfinance('NYSE:C')
    print test
    
        
        