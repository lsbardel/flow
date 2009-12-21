from jflow.core import dates
from jflow.core.field import fieldproxy
from jflow.utils.decorators import lazyattr

from rate import rdate

__all__ = ['scalarrate','ccyrate']

class scalarrate(rdate):
    '''
    A simple scalar rate.
    A scalar rate define the building-block for composite rates
    '''
    def __init__(self, id = None, dte = None, inst = None, holder = None):
        '''
         - id     is an object which must have the following properties
                        code                  string or unicode
                        default_field()       default field code (object or string)
                  and the following method
                        values(dte)           values for date 'dte' 
                        livevalue(livehandle) get the live value
                
         - dte    a datetime instance or None
         - inst   a financial instrument object
        '''
        super(scalarrate,self).__init__(dte = dte, holder = holder)
        self.__id      = id
        self.__inst    = inst
        self.__data    = {}
        self.livefeeds = {}
        
    def __get_id(self):
        return self.__id
    id = property(fget = __get_id)
    
    def __get_inst(self):
        return self.__inst
    inst = property(fget = __get_inst)
    
    def _code(self):
        return str(self.__id.code)
    
    def __get_vendorid(self):
        return self.id.get_vendorid(live = self.live)
    vendorid = property(fget = __get_vendorid)
    
    def __get_data(self):
        '''
        Fetch live and historical data
        '''        
        if self.live:
            return self.register_live_data()
        else:
            return self.__data
    data = property(fget = __get_data)
    
    def __getitem__(self, field = None):
        return self.data.get(field,None)
    
    def __setitem__(self, field, val):
        '''
        Set a field value and notify observers
        '''
        self.__data[field] = val
        self.notify()
        
    def get(self, field = None, vendor = None, **kwargs):
        data = self.data
        
        if data == None:
            return None
        else:
            if isinstance(field,fieldproxy):
                return field.value(self)
            elif field == None:
                id    = self.__id
                field = self.__id.default_field()
            return data.get(field,vendor)
        
    def _get(self, field):
        data = self.data
        if data == None:
            return None
        else:
            return data.get(field,None)
    
    def register_live_data(self):
        '''
        Live data handler
        '''
        if not self.livefeeds:
            id    = self.__id
            vid   = self.vendorid
            if vid:
                ci = vid.vendor.interface()
                if ci:
                    ci.registerlive(self)
        return self.__data
            
    def update_me(self, args):
        self.__data = args
        return self
    
    def _available(self):
        try:
            float(self.get())
            return True
        except:
            return False
        
    def clearlive(self, live_key):
        self.livefeeds.pop(live_key,None)
    
    


class ccyrate(scalarrate):
    '''
    A specialization of a scalar rate.
    '''
    def __init__(self, ccy = None, *args, **kwargs):
        super(ccyrate,self).__init__(*args, **kwargs)
        self.ccy = ccy

