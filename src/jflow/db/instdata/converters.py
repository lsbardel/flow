import datetime
from dateutil.parser import parse as dataparse
from ccy import future_month_list


class Converter(object):
    cdict = {}
    def get_or_create(self, val, **kwargs):
        return self.cdict.get(val,val)

class CurrencyCreator(Converter):
    
    def get_or_create(self, val, **kwargs):
        from jflow.db.geo import currency
        c = currency(val)
        if c:
            return c.code
        else:
            raise ValueError('Currency %s not recognized' % val)

class CountryCreator(Converter):
    
    def get_or_create(self, val, **kwargs):
        from jflow.db.geo import country_map
        c = country_map(val)
        if c:
            return c
        else:
            raise ValueError('Country %s not recognized' % val)

class VendorCreator(Converter):
    
    def get_or_create(self, val, **kwargs):
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
             '30/360 NON-EOM': '30360',
             'ACT/365': 'act365',
             'NL/365': 'act365',
             'BUS DAYS/252':'bd252'}
    def get_or_create(self, val, **kwargs):
        r = self.cdict.get(val,None)
        if r is None:
            raise ValueError("The day count %s is not supported" %val)
        
        return r
    
    
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
    
    def get_or_create(self, val, **kwargs):
        from jflow.db.instdata.models import Exchange
        if val:
            code = self.cdict.get(val,val)
            code = code[:12]
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
    def get_or_create(self, val, **kwargs):
        if val:
            try:
                v = int(val)
                if v in [1,2]:
                    return v
                else:
                    return 3
            except:
                val = val.lower()
                return self.cdict.get(val.lower(),3)
        else:
            return 3

#### Added different date convert method as dataparse assumes that the date is in US Format
#rather than checking Locale
######

def fromUKdt(strdt):
    d , mo , yr = strdt.split(' ')[0].split('/')
    d = int(d)
    mo = int(mo)
    
    if len(yr) <> 4:
        raise TypeError,"A 4 digit year is required"
    
    yr = int(yr)
    return datetime.datetime(yr,mo,d)

class BondDate(Converter):                  
    
    def get_or_create(self, val, **kwargs):
        if isinstance(val,datetime.date):
            return val
        if val:
            try:
                return fromUKdt(val).date()
            except Exception , e:
                pass
            
            try:
                return dataparse(val)
            except:
                return None
        else:
            return None
        
########################    
    
class CollateralCreator(Converter):                  
    
    def get_or_create(self, val, **kwargs):
        from jflow.db.instdata.models import CollateralType
        if val:
            obj, created = CollateralType.objects.get_or_create(name = val)
            return obj
        else:
            raise ValueError('Collateral Type not specified')

class BondclassCreator(Converter):
    
    def get_or_create(self, bondcode,
                      curncy = '',
                      country='',
                      convertible = None,
                      **kwargs):
        from jflow.db.instdata.models import BondClass
        if not bondcode:
            raise ValueError("Bondcode not provided")
        objs = BondClass.objects.filter(bondcode = bondcode)
        N = objs.count()
        if convertible:
            convertible = True
        else:
            convertible = False
        if N:
            obj = objs.filter(country=country,
                              curncy=curncy,
                              convertible=convertible,
                              **kwargs)
            if obj:
                return obj[0]
        
        code = bondcode
        if N:
            code = '%s_%s' % (bondcode,N)
        obj = BondClass(code = code,
                        bondcode = bondcode,
                        country=country,
                        curncy=curncy,
                        convertible=convertible,
                        **kwargs)
        obj.save()
        return obj


class FutureContractConverter(Converter):
    
        
    def _get_future_code(self , code):
        blbs = code.split(' ')
        if len(blbs) == 1:
            raise ValueError("blb code %s is not recognised" %blbs)
        blbc = '_'.join(blbs[:-1])
        N = len(blbc)
        if N < 4:
            raise ValueError("blb code %s is not recognised" %blbs)
        p = 2
        mc = blbc[N-p]
        if mc not in future_month_list:
            p = 3
            mc = blbc[N-p]
            if mc not in future_month_list:
                raise ValueError("blb code %s is not recognised" %mc)
        cona = blbc[:-p]
        return cona.upper()
    
    def get_or_create(self, code):
        if not code:
            raise ValueError("Futures code not provided")
        
        fcode = self._get_future_code(code)
        from jflow.db.instdata.models import FutureContract
        
        contracts = FutureContract.objects.filter(code = fcode)
        if contracts:
            return contracts[0]
        else:
            raise ValueError("The future contract code %s is not in the database" %fcode)
    
    

_c = {'exchange':ExchangeCreator(),
      'daycount':DayCountCreator(),
      'curncy': CurrencyCreator(),
      'country': CountryCreator(),
      'vendor': VendorCreator(),
      'security_type': SecurityType(),
      'bonddate': BondDate(),
      'collateral': CollateralCreator(),
      'bondclass': BondclassCreator(),
      'future_contract' : FutureContractConverter()}

def convert(key,value, **kwargs):
    cc = _c.get(key,None)
    if cc:
        return cc.get_or_create(value,**kwargs)
    else:
        return value