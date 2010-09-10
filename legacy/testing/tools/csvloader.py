import csv

from django.db.models import Q

from djpcms.core.exceptions import ObjectDoesNotExist

import jflow.db.trade.models as trade
from jflow.db.instdata.scripts import instrument

from firm_code_load import *
from base import *

__all__ = ['csvloader','loadcsv']


class PositionError(Exception):
    
    def __init__(self, fund, e, r):
        self.fund  = fund
        self.descr = r['Description']
        self.msg   = str(e)
        
    def __str__(self):
        return 'Position %s error in Fund %s: %s' % (self.descr,self.fund,self.msg)
        


class csvloader(loader):
    ''' 
    Loads data from correctly prepared csv files to database. Column headings in 
    files and field names in relevant database tables must match exactly.
    '''
    def __init__(self, *args, **kwargs):
        super(csvloader,self).__init__(*args, **kwargs)
        self.connect()
        
    def connect(self):
        if isinstance(self.conn_string,str):
            io1 = open(self.conn_string,'r')
        else:
            io1 = self.conn_string
        self.res = csv.DictReader(io1)
        
    def doload(self):
        res         = self.res
        self.failed = 0
        self.done   = 0
        for r in res:
            try:
                self.loadrow(r)
            except Exception, e:
                self.unhandled_errors.append(str(e))
                #self.msgs.saverror(e)
                
    def loadrow(self, r):
        raise NotImplementedError

    def process_instrument(self, r):
        '''
        Add skeleton data for fund, ETF or equity instrument.
        '''
        try:
            vnd  = self.vendors[r.pop('default_vendor',None).lower()]
        except:
            vnd  = self.vendors['blb']
        model = r.pop('model','').lower()
        ic = None
        code = None
        
        if model:
            id, r, model  = self.instHandler[model](r, model, vnd)
            if isinstance(id,jmodels.DataId):
                ic = id.ic
            else:
                ic   = id
                code = ic.code
                
            if ic:
                ity = ic.instype
                if ity:
                    if ity != model:
                        ic.delete()
                        ic = None
                    else:
                        ic.delete_instrument()
            
                                
            if ic:
                instrument.MakeInstrument(ic, **r)
            else:
                instrument.Make(dataid = id, code = code, model = model, **r)
        else:
            id = self.makeId(r, vnd)
            self.makeVendorIds(id,r)
        
        return id
            
    def process_fundmanager(self, r):
        '''
        Add or update jflow_fundmanager records.
        '''
        code = r['manager'].upper()
        obj  = jmodels.FundManager.objects.get_or_create(code = r['manager'].upper())[0]
        obj.name = r['name']
        obj.description = r['description']
        obj.address = r['address']
        obj.website = r['website']
        obj.save()
        return obj
        
    def process_tseries(self, r):    
        '''
        Add time series data to jflow_mktdata. Assumes that the data being added
        will be added to 
        '''
        fields = self.fields
        date = DateFromString(r['Date'])
        del r['Date']
        
        if not fields:
            for k in  r:
                fields[k] = jmodels.DataField.objects.get(code = k)
        
        for k,v in  r.iteritems():
            f = fields[k]
            try:
                v = float(v)
                obj = jmodels.MktData(vendor_id = self.vid, field = f, dt = date, mkt_value = v)
                obj.save()
            except:
                pass
        return obj
        
    def process_netikpos(self, r):
        '''
        Create position history for trade_date from Netik extract.
        '''
        # Get the fund code associated with the IAM internal portfolio code
        fund = trade.Fund.objects.get(firm_code = r['FundID'])
        
        icode = r['IAMID']
        try:
            # Get the instrument code associated with IAM internal instrument ID
            ic = instrument_from_firm_code(icode)
        except Exception, e:
            # Instrument not available try to create one
            try:
                ic = create_auto_instrument(icode,r)
            except:
                raise PositionError(fund,e,r)
            
        try:
            # Get the associated trade date (assumed positions are COB on this date)
            trade_date = r['PositionDate'].replace('/','.')
            trade_date = DateFromString(trade_date).date()
        
            msgs     = self.msgs
            if msgs.rel_date:
                if trade_date != msgs.rel_date:
                    raise ValueError, "Mismatch in position date"
            else:
                msgs.rel_date = trade_date
        
            # Default custodian set for fund; will fail if this isn't set
            custodian = trade.CustodyAccount.objects.filter(fund = fund)
            if custodian.count():
                custodian = custodian[0]
            else:
                raise ObjectDoesNotExist, "Custodian account does not exists"
        
            # Filter the position
            postn = trade.Position.objects.filter(Q(instrumentCode = ic),
                                                  Q(fund           = fund),
                                                  Q(custodian      = custodian),
                                                  Q(status__gt     = 0),
                                                  Q(open_date__lte = trade_date),
                                                  Q(close_date__gt = trade_date) | Q(close_date__isnull=True))
        
            if postn.count() == 0:
                # Is new position
                postn = trade.Position(instrumentCode = ic,
                                       fund           = fund,
                                       custodian      = custodian,
                                       open_date      = trade_date)
                postn.save()
            elif postn.count() == 1:
                # Is existing position
                postn = postn[0]
            else:
                raise ValueError, "There are %s conflicting positions %s in %s" % (ic,fund)
        
            '''
            Position created or found now add its position history
            '''
            inst = ic.instrument()
            m    = inst.get_multiplier()
            n  = r['Nominal']   # Position size
            q  = Decimal(n)
            qf = float(n)
            
            cost_unit_local = safeget(r,'CostPerUnitLocal',0)   # traded price local currency
            book_cost_local = safeget(r,'BookCostLocal',0)
            cost_unit_base  = safeget(r,'CostPerUnitBase',0)     # traded price base currency
            book_cost_base  = safeget(r,'BookCostBase',0)
            value_local     = qf*cost_unit_local
            value_base      = qf*cost_unit_base
            
            obj = trade.PositionHistory.objects.filter(position = postn,
                                                       dt = trade_date)
            if obj.count():
                obj                = obj[0]
                obj.size           = q
                obj.value          = value_local
                obj.dirty_value    = book_cost_local
                obj.book_cost_base = book_cost_base
                obj.cost_unit_base = cost_unit_base
            else:
                obj = trade.PositionHistory(position       = postn,
                                            dt             = trade_date,
                                            size           = q,
                                            value          = value_local,
                                            dirty_value    = book_cost_local,
                                            book_cost_base = book_cost_base,
                                            cost_unit_base = cost_unit_base)
            obj.save()
            return obj
        except Exception, e:
            raise PositionError(fund,e,r)

            
def loadcsv(filename = None,
            datatype = None,
            code = None,
            verbose = 1,
            username = None,
            password = None):

    if filename == None:
        filename ='D:/matdb/NetikPosTest3.csv' 
        datatype = 'netikpos'
        
    datatype = datatype.lower()
    
    if datatype in ('fund', 'etf', 'equity'):
        datatype = 'instrument'
    elif datatype in ('fundmanager', 'fund_manager', 'manager'):
        datatype = 'fundmanager'
    elif datatype in ('tseries', 'ts'):
        datatype = 'tseries'
    elif datatype in ('netikpos'):
        datatype = 'netikpos'    
    else:
        raise NotImplementedError
    # Note you can use the Unix forward slash '/' instead of '\\' in filename.
    r = csvloader(connection = filename,
                  datatype = datatype,
                  code = code,
                  verbose = verbose,
                  username = username,
                  password = password)
    r.load()

if __name__ == '__main__':
    loadcsv()

    