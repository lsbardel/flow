from djpcms.core.exceptions import ObjectDoesNotExist

from jflow.db.instdata.models import InstrumentCode, numeric_code
from jflow.db.instdata.scripts import instrument
from jflow.core.dates import DateFromString

__all__ = ['num_code',
           'instrument_from_firm_code',
           'create_auto_instrument',
           'safeget']

auto_codes = {'CUX':'fwdcash',
              'NGF':'depo',
              'NGP':'bill'}


def num_code(fc):
    try:
        nc = numeric_code(fc)
        return InstrumentCode.objects.get(firm_code = str(nc))
    except:
        return None 


def instrument_from_firm_code(firm_code):
    fc = num_code(firm_code)
    if not fc:
        try:
            return InstrumentCode.objects.get(firm_code = firm_code)
        except:
            raise ObjectDoesNotExist, 'Firm code %s not found' % firm_code
    else:
        return fc
    

def create_auto_instrument(code,data):
    for k,model in auto_codes.items():
        if code.rfind(k) == 0:
            return InstCreator(code,model).create(data)
    raise ValueError

def safeget(r,code,def_val):
    try:
        return float(r.get(code,def_val))
    except:
        return def_val


class InstCreator(object):

    def __init__(self, code, model):
        self.code  = code
        self.model = model
    
    def create(self,r):
        func = getattr(self,'create_%s' % self.model,None)
        if func:
            return func(r,self.model)
        else:
            raise ValueError
        
    def create_fwdcash(self, r, model):
        dt = DateFromString(r['MaturityDate']).date()
        cu = r['AssetCurrency']
        return instrument.Make(code = self.code, firm_code = self.code,
                               curncy = cu, value_date = dt, model = model)
    
    def create_depo(self, r, model):
        return create_fwdcash(r,model)
            