import datetime

from django.core.exceptions import ObjectDoesNotExist

from jflow.db.instdata.models import VendorId, FutureContract, Exchange, CollateralType
from base import instrumentLoader, exercise_type_dict, equity_type_dict

__all__ = ['BlbInstLoader',
           'BlbFutureLoader',]



_blbex = {'ASX':'ASX',
          'Athens': 'ASE',
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

_blb_day_count = {'ACT/ACT': 'actact',
                  'ACT/ACT NON-EOM': 'actact',
                  'ACT/360': 'act360',
                  '30/360': '30360',
                  'ISMA-30/360': '30360',
                  'ISMA-30/360 NONEOM': '30360',
                  'ACT/365': 'act365',
                  'NL/365': 'act365',
                  'BUS DAYS/252':'bd252'}


def DateFromBlbString(ds):
    try:
        dds = ds.split('/')
        return datetime.date(year = int(dds[2]), month = int(dds[1]), day = int(dds[0]))
    except:
        return None

def get_future_year(y):
    if y < 50:
        return 2000 + y
    else:
        return 1900 + y



class BlbInstLoader(instrumentLoader):
    source     = "bloomberg"
    vendorcode = 'blb'
    
    def __init__(self, model, data):
        self.blbticker   = data.get('blb',None)
        data['exercise'] = exercise_type_dict.get(data.get('exercise_type',''), 2)
        data['security_type'] = equity_type_dict.get(data.pop('security_type',''),1)
        super(BlbInstLoader,self).__init__(model, data)
        
    def parse_exchange(self, code):
        if code:
            c = _blbex.get(code,None)
            if c:
                try:
                    return Exchange.objects.get(code = c)
                except:
                    return None
            else:
                return None
        else:
            return None
    
    def futuredata(self, data):
        from jflow.core.finins import future_month_list, future_month_dict
        blbs = self.blbticker.split(' ')
        if len(blbs) == 1:
            raise ValueError("Unrecognized blb code")
        blbc = '_'.join(blbs[:-1])
        N = len(blbc)
        if N < 4:
            raise ValueError("Unrecognized blb code")
        p = 2
        mc = blbc[N-p]
        if mc not in future_month_list:
            p = 3
            mc = blbc[N-p]
            if mc not in future_month_list:
                raise ValueError("Unrecognized blb code")
        yy   = get_future_year(int(blbc[-p+1:]))
        cona = blbc[:-p]
        try:
            co = FutureContract.objects.get(code = cona)
        except:
            raise ObjectDoesNotExist("Future contract %s not in database" % cona)
        mn = future_month_dict[mc]
        ed = datetime.date(year = yy, month = mn[0], day = 1)
        data['contract']       = co
        data['expiry']         = ed
        data['first_trade']    = DateFromBlbString(data.get('first_trade',None))
        data['last_trade']     = DateFromBlbString(data.get('last_trade',None))
        data['first_notice']   = DateFromBlbString(data.get('first_notice',None))
        data['first_delivery'] = DateFromBlbString(data.get('first_delivery',None))
        data['last_delivery']  = DateFromBlbString(data.get('last_delivery',None))
        super(BlbInstLoader,self).futuredata(data)
    
        
    def bondclass(self, data):
        sn = data.pop('securityname',None)
        if not sn:
            raise ValueError('"security_name" not provided')
        sns = sn.split(' ')
        
        data['bond_class_code'] = sns[0]
        
        if self.group and self.group.code == 'sovereign':
            data['sovereign'] = True
        
        day_count = data.pop('day_count',None)
        data['day_count'] = _blb_day_count[day_count]
        
        cn = data.get('collateral_type',None)
        if cn:
            try:
                ct = CollateralType.objects.get(name = cn)
            except:
                ct = CollateralType(name = cn, order = 10000)
                ct.save()
        else:
            ct = CollateralType.objects.get(name = 'UNDEFINED')
        data['collateral_type'] = ct
        return super(BlbInstLoader,self).bondclass(data)
        
    def make_equity_code(self, data):
        blb = data.get('blb',None)
        if blb:
            blbs = blb.split(' ')
            if len(blbs) > 1:
                return '_'.join(blbs[:-1])
            else:
                return blb
        else:
            return None
        
    def get_dataid(self, key, data):
        issuer = data.pop(key,None)
        if not issuer:
            return None
        blbcode = '%s Equity' % issuer
        vid = VendorId.objects.filter(ticker = blbcode, vendor = self.vendorload)
        if vid:
            return vid[0].dataid
        else:
            return None
        
    def get_date(self, key, data):
        return DateFromBlbString(data.pop(key,None))
    
    