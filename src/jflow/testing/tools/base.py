from django.contrib.contenttypes.models import ContentType

from decimal import Decimal

from jflow.db.instdata import models as jmodels
from jflow.db.trade import models as trademodels
from jflow.db.instdata.scripts.dataid import dataidhandler
from jflow.core.dates import DateFromString

from jflow.db.geo import ccypair
from jflow.core.finins import date_to_code

from djpcms.db.interfaces import save_and_log

from extra import loadermsg, closepositions

dataidhand = dataidhandler()





class loader(object):
    '''
    Class object for loading routines.
    There are four upload routines:
        1. skeleton instrument (fund, ETF, equity) creation;
        2. supplementary information upload for fund manager;
        3. time series data load for individual instruments;
        4. position and position history upload from Netik data dump.  
    '''
    local_vendor    = 'manual'
    
    def __init__(self, user = None, connection = None,
                 datatype   = None, code       = None,
                 verbose    = 1, **kwargs):
        '''
        connection: a connection string
        datatype:   instrument for fund, etf or equity upload; 
                    manager    for fund manager upload;
                    tseries    for timeseries upload;
                    netikpos   for Netik position data upload.
        code:       is the DataId code (only required for time series upload) 
        '''
        self.user        = user
        self.conn_string = connection
        self.vendors     = dataidhand.vendors()
        self.msgs        = loadermsg(user)
        self.unhandled_errors = []
        
        #if datatype == 'tseries':
        #    ct        = ContentType.objects.get_for_model(jmodels.MktData)
        #    self.vid  = self.get_vendorid(code)
        #    if self.vid == None:
        #        raise ValueError, "No data id available for data"
        #    self.fields = {}
        #elif datatype == 'instrument':
        #    ct            = ContentType.objects.get_for_model(jmodels.InstrumentCode)
        #    d = {'future':  self.handleFuture,
        #         'equity':  self.handleEquity,
        #         'etf':     self.handleEquity,
        #         'fund':    self.handleEquity,
        #         'bond':    self.handleBond,
        #         'cash':    self.handleCash,
        #         'forex':   self.handleCash}
        #    self.instHandler = d
        #elif datatype == 'netikpos':
        #    ct            = ContentType.objects.get_for_model(trademodels.Position)
        #    self.msgs     = closepositions(user)
        #else:
        #    raise NotImplementedError
        #
        #self.msgs.content_type = ct
        self.verbose           = verbose
        
    def get_vendorid(self, code):
        if code == None:
            return None
        code = jmodels.TrimCode(code)
        id = jmodels.DataId.objects.get(code = code)
        vd = self.vendors.get(self.local_vendor,None)
        return dataidhand.make_vendorid(code,vd,id)
        
    def getFunction(self,datatype):
        f = getattr(self,'%s_%s' % (self.prefix,datatype), None)
        if f == None:
            raise ValueError, 'Function %s does not exist' % datatype
        return f
        
    def load(self):
        self.doload()
        self.msgs.wrapload()            
        if self.verbose > 0:
            print 'created %s record(s)' % self.done
            print 'failed to create %s record(s)' % self.failed
            
    def doload(self):
        pass
    
    def process_instrument(self, *args):
        pass
    
    def process_fundmanager(self, *args):
        pass
    
    def process_tsdata(self, *args):
        pass
    
    def makeVendorIds(self, id, r):
        return dataidhand.make_or_update_vendors(id,r)
        
    def makeId(self, r, vnd):
        is_live = True
        if r.pop('live',1) == 0:
            is_live = False
        code    = r.pop('code')
        country = r.pop('country','').upper()
        tags    = r.pop('tags','')
        id = jmodels.DataId.objects.filter(code = code)
        
        if id.count():
            id = id[0]
            id.name = r.pop('name','')
            id.description = r.pop('description','')
            id.country = country
            id.tags    = tags
            save_and_log(id,self.user,"updated form csv file")
        else:
            id = jmodels.DataId(code = code,
                        name = r.pop('name',''),
                        description = r.pop('description',''),
                        country = country,
                        tags    = tags,
                        live = is_live,
                        default_vendor = vnd)
            save_and_log(id,self.user,"loaded form csv file")
        return id
    
    def handleFuture(self, r, model, vnd):
        '''
        Create a future DataId
        '''
        co    = jmodels.FutureContract.objects.get(code = r.pop('contract','').upper())
        ed    = DateFromString(r.pop('end_date',None)).date()
        name  = '%s %s' % (co.description,ed.strftime("%b %y"))
        mc    = date_to_code(ed)
        di = {'contract':co,
              'country': co.country,
              'code': '%s%s' % (co.code,mc),
              'firm_code': r.pop('firm_code',''),
              'name': name,
              'description': name,
              'tags': r.pop('tags',''),
              'first_trade': DateFromString(r.get('first_trade',None)).date(),
              'last_trade': DateFromString(r.get('last_trade',None)).date(),
              'first_notice': DateFromString(r.get('first_notice',None)).date(),
              'first_delivery': DateFromString(r.get('first_delivery',None)).date(),
              'last_delivery': DateFromString(r.get('last_delivery',None)).date()}
        id = self.makeId(di, vnd)
        
        self.makeVendorIds(id,r)
        return id, di, model
    
    def handleEquity(self, r, model, vnd):
        '''
        Create an equity DataId
        '''
        ex   = r.pop('exchange',None)
        if ex:
            r['exchange'] = jmodels.Exchange.objects.get(code = ex.upper())
        id = self.makeId(r, vnd)
        self.makeVendorIds(id,r)
        r['multiplier'] = float(r['multiplier'])
        r['curncy'] = r['curncy'].upper()
        if model == 'fund':
            mcode = r.pop('manager',None)
            if not mcode:
                mcode = id.code
            r['manager'] = jmodels.FundManager.objects.get_or_create(code = mcode.upper())[0]
        else:
            r.pop('domicile',None)
            r.pop('manager',None)
            r.pop('status',None)
        return id,r,model
    
    def handleBond(self, r, model, vnd):
        ex   = r.pop('exchange',None)
        if ex:
            r['exchange'] = jmodels.Exchange.objects.get(code = ex.upper())
        co = jmodels.BondClass.objects.get(code = r.pop('bond_class','').upper())
        coupon = Decimal(r.pop('coupon','0'))
        mat    = r.get('maturity_date',None)
        des    = co.fulldescription()
        
        if mat:
            mat  = DateFromString(mat).date()
            mlo  = mat.strftime("%d %b %y")
            code = '%s_%02d%s' % (co.code,mat.month,str(mat.year)[2:])
            name = '%s %s %s' % (co.code,coupon,mlo)
            des  = '%s. Coupon: %s. Expiry: %s' % (des,coupon,mlo)
        else:
            mat = None
            mlo = 'Perpetual'
            code = '%s_perp_%s' % (co.code,coupon)
            name = code
            des  = '%s. Coupon: %s.' % (des,coupon)
        
        code = jmodels.TrimCode(code)
        di = {'bond_class':co,
              'country': co.country,
              'code': code,
              'firm_code': r.pop('firm_code',''),
              'name': name,
              'description': des,
              'coupon': coupon,
              'tags': r.pop('tags',''),
              'ISIN': r.pop('ISIN',''),
              'CUSIP': r.pop('CUSIP',''),
              'maturity_date': mat,
              'announce_date': DateFromString(r.get('announce_date',None)).date(),
              'first_settle_date': DateFromString(r.get('first_settle_date',None)).date(),
              'first_coupon_date': DateFromString(r.get('first_coupon_date',None)).date(),
              'accrual_date': DateFromString(r.get('accrual_date',None)).date()}
        id = self.makeId(di, vnd)
        self.makeVendorIds(id,r)
        return id, di, model
        
    def handleCash(self, r, model, vnd):
        di   = None
        code = None
        ccy1 = r.pop('ccy1').upper()
        ccy2 = r.pop('ccy2','').upper()
        fc   = r.pop('firm_code','')
        if ccy2:
            ccy_pair = ccypair(ccy1+ccy2)
            vd   = DateFromString(r.pop('value_date','')).date()
            code = '%s-%s' % (ccy_pair.code,vd.strftime("%d%b%y"))
            di   = {'ccy_pair':code,
                    'value_date': vd,
                    'model': 'forex',
                    'firm_code': fc}
        else:
            try:
                vd   = DateFromString(r.pop('value_date','')).date()
                di   = {'model': 'fwdcash',
                        'value_date': vd}
                code = fc
            except:
                type  = int(r.pop('type',1))
                di    = {'model': 'cash',
                         'type':   type}
                code  = ccy1+jmodels.cash_code_from_type(type)
            di.update({'curncy': ccy1,'firm_code': fc})
            
        ic = jmodels.InstrumentCode.objects.filter(code = code)
        if ic:
            ic = ic[0]
        else:
            ic = jmodels.InstrumentCode(code = code)
            ic.save()
        return ic, di, model
        
            
            
    def process_netikpos(self, *args):
        pass
    
    def htmlmessage(self):
        r = []
        if self.done > 0:
            r.append('Created %s record(s). ' % self.done)
        if self.failed:
            r.append('Failed to create %s record(s).' % self.failed)
        return '\n'.join(r)
    