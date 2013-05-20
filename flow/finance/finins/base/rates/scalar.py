from jflow.core import dates
from jflow.utils.observer import lazyobject
from jflow.utils.decorators import lazyattr

from rate import rdate
#from feed import Feed

__all__ = ['scalarrate','ccyrate','fixed_income_rate']


class proxyrate(object):
    
    def _get_value_at_date(self, dteobj):
        raise NotImplementedError


class scalarrate(rdate, lazyobject):
    '''
    A simple scalar rate.
    A scalar rate define the building-block for composite rates
    '''
    def __init__(self,
                 id = None,
                 dte = None,
                 inst = None,
                 holder = None,
                 proxy = None):
        '''
         - id     is an object which must have the following properties
                        code                  string or unicode
                        default_field         default field code (object or string)
                  and the following method
                        values(dte)           values for date 'dte' 
                        livevalue(livehandle) get the live value
                
         - dte    a datetime instance or None
         - inst   a financial instrument object
        '''
        rdate.__init__(self, dte = dte, holder = holder)
        lazyrate.__init__(self)
        self.__id     = id
        self.__inst   = inst
        self.__data   = None
        if isinstance(proxy, proxyrate):
            self.__proxy  = proxy
        else:
            self.__proxy  = None
        
    def __get_id(self):
        return self.__id
    id = property(fget = __get_id)
    
    def __get_inst(self):
        return self.__inst
    inst = property(fget = __get_inst)
    
    def _code(self):
        return str(self.__id.code)
    
    def __get_data(self):
        '''
        Fetch live and historical data
        '''
        px = self.__proxy
        if px:
            return px._get_value_at_date(self.dateobj())
        
        if self.live:
            return self.__live_data()
        else:
            data = self.__data
            if data == None:
                data        = self.id.values(self.date)
                self.__data = data
            return data
    data = property(fget = __get_data)
    
    def __getitem__(self, field):
        return self.get(field)
        
    def get(self, field = None):
        data = self.data
        
        if data == None:
            return None
        #
        else:
            id    = self.__id
            if field == None:
                field = id.default_field
            key = str(field).upper().replace(' ','_')
            v   = data.get(key,None)
            if v == None:
                if self.live:
                    v = id.value(dte = self.date, field = field)
                    if v == None:
                        v = self.badvalue
                    data[key] = v
                else:
                    v = self.badvalue
            return v
    
    def __live_data(self):
        if self.__data == None:
            id    = self.__id
            if id.isdummy():
                self.__data = {str(id.default_field): id.value}
            else: 
                lh    = self.liveHandle
                lfeed = id.livevalue(lh)
                if lfeed:
                    lfeed.attach(self)
        return self.__data
    
    @lazyattr
    def __get_feed(self):
        return Feed(self)
    feed = property(fget = __get_feed)
            
    def update_me(self, args):
        self.__data = args
        return args
    
    def _available(self):
        try:
            float(self.get())
            return True
        except:
            return False
    



class ccyrate(scalarrate):
    '''
    A specialization of a scalar rate.
    '''
    def __init__(self, ccy = None, *args, **kwargs):
        super(ccyrate,self).__init__(*args, **kwargs)
        self.ccy = ccy



class fixed_income_rate(scalarrate):
    '''
    A fixed income rate.
    This scalar rate expose the cashflow method used by
    the bootstrapping algorithm of a yield curve
    '''
    def __init__(self, *args, **kwargs):
        super(fixed_income_rate,self).__init__(*args, **kwargs)
        
    @lazyattr
    def __get_cashflow(self):
        inst         = self.inst
        inst.rateobj = self.feed
        cf           = inst.simplecashflow(self.date)
        return cf
    cashflow = property(fget = __get_cashflow)
    
    def __get_internalrate(self):
        v = self.get()
        return self.inst.internalrate(v)
    yieldrate = property(fget = __get_internalrate)
    
    def curve_priority(self):
        return self.inst.curve_priority()
    