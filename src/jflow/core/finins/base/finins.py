
from jflow.core import dates
from jflow.utils.decorators import lazyattr
from jflow.utils.observer import lazyvalue
#from jflow.core.cashflow import CashFlow, fixcash, coupon

from base import PositionBase
from pricer import *


class fhistory(object):
    '''
    historical data of code ''code'' for an instrument
    
    @param inst: instance of finins
    @param code: identifier for the historical data  
    '''
    def __init__(self, inst, code, logger = None):
        self.inst = inst
        self.code = code
        self.ts   = None
        self.logger = logger
        
    def __repr__(self):
        return '%s: history of %s' % (self.inst,self.code)
    
    def __str__(self):
        return self.__repr__() 
        
    def update(self, res):
        self.ts = res
        self.inst.update(self)
        
    def errback(self, err):
        self.err(err)
        
    def log(self, msg):
        if self.logger:
            self.logger.msg(msg)
    
    def err(self, err):
        if self.logger:
            self.logger.err(err)


class finins(PositionBase):
    '''
    Financial instrument base class
        dbobj is an object which expose the following properties/methods
            .open_date()     date
            .instrument()    return an instrument object with the
                             following properties/methods
                ccy()
                country()
                tags()
                
    '''
    notavailable  = '#N/A'
    def __init__(self,
                 details        = None,
                 dbobj          = None,
                 inst           = None,
                 code           = None,
                 value_date     = None,
                 calc_date      = None,
                 append_to_code = '',
                 **kwargs):
        self.holding       = details
        self.__pricer      = None
        self.__value_date  = value_date
        self.rateobj       = None
        self.calc_date     = dates.get_livedate(calc_date)
        self.mktprice      = self.notavailable
        self.jsonvals      = None
        self.histories     = {}
        if inst:
            self.__instrument = inst
        else:
            self.__instrument = dbobj.instrument()
        if code == None:
            code = str(self.dbinstrument.code)
        code = '%s%s' % (code, append_to_code)
        super(finins,self).__init__(dbobj = dbobj, code = code, **kwargs)
        
    def name(self):
        return self.__instrument.name()
    
    def multiplier(self):
        try:
            return self.__instrument.get_multiplier()
        except:
            return 1.0
        
    def __get_iscash(self):
        return self.__instrument.iscash()
    iscash = property(fget = __get_iscash)
    
    def __get_data_id(self):
        return self.__instrument.get_data_id()
    data_id = property(fget = __get_data_id)
    
    def rate_klass(self):
        return None
    
    def __get_type(self):
        return str(self.__instrument.instype())
    type = property(fget = __get_type)
    
    def end_date(self):
        return self.__instrument.end_date()
    
    def ccy(self):
        return self.__instrument.ccy()
    
    def country(self):
        return self.__instrument.country()
    
    def notional(self, size = 1):
        return float(self.__instrument.tonotional(size))
    
    def nav(self, size = 1):
        try:
            p = float(self.mktprice)
            s = float(size)
            return int(p*self.multiplier()*s)
        except:
            return self.notavailable
    
    def tags(self):
        return self.__instrument.tags()
    
    def mktvalue(self):
        p = self.mktprice
        s = float(self.size)
        if p:
            return int(p*self.multiplier()*s)
        else:
            return '#NA'
    
    def traded(self):
        return self.holding.traded_price()
    
    def book_cost_base(self):
        return self.holding.book_cost_base
    
    def book_cost_local(self):
        return self.holding.book_cost_local
    
    def __get_size(self):
        return self.holding.size
    size = property(fget = __get_size)
    
    def __get_value(self):
        return self.__dirty_value
    value = property(fget = __get_value)
    
    def __get_dbinstrument(self):
        return self.__instrument
    dbinstrument = property(fget = __get_dbinstrument)
    
    def __set_pricer(self, pricer):
        self.__pricer = pricer
    def __get_pricer(self):
        return self.__pricer
    pricer = property(fget = __get_pricer, fset = __set_pricer)
    
    def update_me(self, args):
        '''
        just got an update
        '''
        from jflow.core.rates.objects import Rate
        if isinstance(args,Rate):
            p = self.__pricer
            if p:
                p.calculate(self, args)
        elif isinstance(args,fhistory):
            p = self.__pricer
            if p:
                p.calculate(self, args)
        else:
            return None
        return self
    
    def addhistory(self, code, logger = None):
        '''
        Add historical time series for pricing
        
        @param code: A code indicating the type of history ('price','volume',etc..)
        @return: An instance of fhistory 
        '''
        fhist = self.histories.get(code, None)
        if fhist == None:
            fhist = fhistory(self, code, logger = logger)
            self.histories[code] = fhist
        return fhist


class future_instrument(object):
    pass

class value_date_plugin(object):
    
    def __init__(self, value_date, required = True):
        if not isinstance(value_date, dates.date) and required:
            raise TypeError, '%s not a valid date' % value_date
        self.__value_date = value_date
        
    def __get_value_date(self):
        return self.__value_date
    value_date = property(fget = __get_value_date)
    
    def __get_value_date_string(self):
        vd = self.value_date
        if vd:
            return ' vd %s' % vd.strftime('%d %b %Y')
        else:
            return ''
    value_date_string = property(fget = __get_value_date_string)
    
        
             

    