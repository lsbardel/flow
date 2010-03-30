import datetime
from jflow.db.instdata.models import FutureContract, Exchange
from jflow.db.instdata.loader import instrumentLoader
from instrument import addfuture as _addfuture



_blbex = {'Athens': 'ASE',
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



class BlbInstLoader(instrumentLoader):
    
    def __init__(self, data):
        super(BlbInstLoader,self).__init__(data)
        self.blbticker  = data.get('bloomberg',None)
        
    def parse_exchange(self, code):
        if code:
            c = _blbex.get(code,None)
            if c:
                try:
                    return Exchange(code = c)
                except:
                    return None
            else:
                return None
        else:
            return None


    
    
def DateFromBlbString(ds):
    dds = ds.split('/')
    return datetime.date(year = int(dds[2]), month = int(dds[1]), day = int(dds[0]))


    
def get_future_year(y):
    if y < 50:
        return 2000 + y
    else:
        return 1900 + y
    
    
def addblbfuture(bloomberg,
                 first_trade,
                 last_trade,
                 first_notice,
                 first_delivery,
                 last_delivery,
                 firm_code):
    from jflow.core.finins import future_month_list, future_month_dict
    blbs = bloomberg.split(' ')
    if len(blbs) == 1:
        return "Unrecognized blb code"
    blbc = '_'.join(blbs[:-1])
    N = len(blbc)
    if N < 4:
        return "Unrecognized blb code"
    p = 2
    mc = blbc[N-p]
    if mc not in future_month_list:
        p = 3
        mc = blbc[N-p]
        if mc not in future_month_list:
            return "Unrecognized blb code"
    yy   = get_future_year(int(blbc[-p+1:]))
    cona = blbc[:-p]
    try:
        co = FutureContract.objects.get(code = cona)
    except:
        raise ObjectDoesNotExist("Future contract %s not in database" % cona)
    mn = future_month_dict[mc]
    ed = datetime.date(year = yy, month = mn[0], day = 1)
    first_trade    = DateFromBlbString(first_trade)
    last_trade     = DateFromBlbString(last_trade)
    first_notice   = DateFromBlbString(first_notice)
    first_delivery = DateFromBlbString(first_delivery)
    last_delivery  = DateFromBlbString(last_delivery)
    return _addfuture(co,ed,first_trade,last_trade,first_notice,first_delivery,
                      last_delivery,firm_code, blb = bloomberg)
    
    
class BondLoader(BlbInstLoader):
    
    def __init__(self, data):
        super(BondLoader,self).__init__(data)
        self.bclass = self.bondclass()
        
    def bondclass(self, data):
        sn = data.get('securityname',None)
        sns = sn.split(' ')
        return None
        