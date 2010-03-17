

class Converter(object):
    cdict = {}
    def get_or_create(self, val):
        return self.cdict.get(val,val)        

class ExchangeCreator(Converter):
    cdict = {'Athens': 'ASE',
             'BrsaItaliana': 'BIT',
             'AN Amsterdam': 'ENAM',
             'EN Paris': 'PAR',
             'Hong Kong': 'HKEX',
             'London':'LSE',
             'Korea SE':'KSE',
             'Mexico':'BMV',
             'New York':'NYSE',
             'NASDAQ GS':'NASDAQ',
             'Oslo': 'OSLO',
             'SIX Swiss Ex': 'SIX',
             'Taiwan':'TWSE',
             'Tel Aviv': 'TASE',
             'Tokyo': 'TSE',
             'Toronto':'TSX',
             'Xetra': 'XTA'}
    
    def get_or_create(self, val):
        from jflow.db.instdata.models import Exchange
        code = self.cdict.get(val,val)
        obj, created = Exchange.objects.get_or_create(code = code)
        return obj
    

_c = {'exchange':ExchangeCreator()}

def convert(key,value):
    cc = _c.get(key,None)
    if cc:
        return cc.get_or_create(value)
    else:
        return value