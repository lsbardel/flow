

class Converter(object):
    cdict = {}
    def get_or_create(self, val):
        return self.cdict.get(val,val)        

class CurrencyCreator(Converter):
    
    def get_or_create(self, val):
        from jflow.db.geo import currency
        c = currency(val)
        if c:
            return c.code
        else:
            raise ValueError('Currency %s not recognized' % val)

class CountryCreator(Converter):
    
    def get_or_create(self, val):
        from jflow.db.geo import country
        c = country(val)
        if c:
            return val
        else:
            raise ValueError('Country %s not recognized' % val)

class VendorCreator(Converter):
    
    def get_or_create(self, val):
        from jflow.db.instdata.models import Vendor
        if isinstance(val,Vendor):
            return val
        else:
            try:
                return Vendor.objects.get(code = val.upper())
            except:
                raise ValueError('Vendor %s not available' % val)
        

class DayCountCreator(Converter):
    cdict = {'ACT/ACT': 'actact',
             'ACT/ACT NON-EOM': 'actact',
             'ACT/360': 'act360',
             '30/360': '30360',
             'ISMA-30/360': '30360',
             'ISMA-30/360 NONEOM': '30360',
             'ACT/365': 'act365',
             'NL/365': 'act365',
             'BUS DAYS/252':'bd252'}
    
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
        if val:
            code = self.cdict.get(val,val)
            obj, created = Exchange.objects.get_or_create(code = code)
            return obj
        else:
            return None
    
class SecurityType(Converter):
    cdict = {'common stock': 1,
             'stock': 1,
             'common': 1,
             'right issue': 2,
             'right': 2}
    def get_or_create(self, val):
        if val:
            try:
                v = int(val)
                if v in [1,2]:
                    return v
                else:
                    return 3
            except:
                val = val.lower()
                return cdict.get(val.lower(),3)
        else:
            return 3          


_c = {'exchange':ExchangeCreator(),
      'curncy': CurrencyCreator(),
      'country': CountryCreator(),
      'vendor': VendorCreator(),
      'security_type': SecurityType()}

def convert(key,value):
    cc = _c.get(key,None)
    if cc:
        return cc.get_or_create(value)
    else:
        return value