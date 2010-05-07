
import base
#from fx import *
#from future import *



class Factory(base.cacheObject):
    '''
    Factory class for rate factories.
    This class is responsible for generating Rate factory classes.
    Its method select is called by the rate-cache when a new rate
    factory class is required.
    '''
    def __init__(self, codes, getid):
        self.codes       = codes
        self.scalar      = base.scalarFactoryFactory()
        #self.fx          = fxfactory(self.cache,codes.fx_cross_code)
        #self.futurecurve = futurecurve(holder = self.cache,
        #                               code = codes.future_curve_code,
        #                               yccode = codes.yield_curve_code)
        self.get_id       = getid
        self.get_currency = self.cache.get_currency
    
    def select(self, code):
        self.logger.debug('selecting constructor for %s rate' % code)
        N = len(code)
        
        # Check the easy rates first
        #if code == self.fx._code:
        #    return self.fx
        
        # If N == 6 check special codes
        if N>=5 and N<=6:
            return self.selectSpecial(code, N)
        
        # Standard scalar rate
        else:            
            return self.get_scalar(code, N)
    
    
    def selectSpecial(self, code, N):
        M      = N - 3;
        co     = code[:M]
        suffix = code[M:]
        
        return self.get_scalar(code, N)
    
        #if suffix == self.codes.yield_curve_code:
        #    suffix = self.codes.default_curve_code
        
        # Check if this is a future contract
        if suffix == self.futurecurve.klasscode:
            cur = get_currency(co)
            if cur:
                co = cur.future
            return self.get_futurecurve(co)
        else:
            return self.get_scalar(code, N)
        
    
    def get_futurecurve(self, code):
        return self.futurecurve.get(contract = code)
    
    
    def get_scalar(self, code, N):
        '''
        Create a scalar rate
        '''
        id         = None
        proxy      = None
        ccy        = None
        kwargs     = {}
        
        # First check if this is a currency
        if N == 3:
            try:
                ccy = self.get_currency(code)
            except:
                ccy = None
            if ccy:
                if code == 'USD':
                    return None
                else:
                    id = self.get_id(code)
        
        if id == None:
            # Try a dataid
            id = self.get_id(code)
        
        if id == None and N == 6:
            # Check if it is a currency pair
            c1  = self.get_currency(code[:3])
            c2  = self.get_currency(code[3:])
            if c1 and c2 and c1 != c2:
                #fxhistory = self.cache.get_rate_holder(self.fx._code)
                return base.ccypairFactory(c1, c2)
        
        if id == None:
            return None
        
        return self.scalar.get(id = id, proxy = proxy, ccy = ccy)
