from jflow.core.dates import get_livedate
from jflow.core.rates.objects import Rate


__all__ = ['Pricer',
           'sensitivity',
           'PricerNotAvailable']


class PricerNotAvailable(Exception):
    "Pricer not available"
    def __init__(self, element):
        self.element  = str(element)
    
    def __str__(self):
        return 'Pricer not available for %s' % self.element

    
class DifferentDatesError(Exception):
    "Different dates"



class Pricer(object):
    '''
    Base class for pricing financial instrument
    '''
    calcprefix = 'calculator'
    
    def __init__(self, logger = None):
        super(Pricer,self).__init__()
        self.__rates       = {}
        self.__instruments = []
        self.logger        = logger
        
    def __repr__(self):
        return '%s' % self.__class__.__name__
    
    def __str__(self):
        return self.__repr__()
        
    def loadhistory(self, fin, get_data, start = None, end = None):
        '''
        load market data for financial instrument 'fin'
        
        @param fin: Instance of finins (jflow.core.finins)
        @param get_data: function used to upload data
        @param start: start date of data. Instance of datetime.date
        @param end: end date of data. Instance of datetime.date
        '''
        rates = self.get_rates(fin)
        for k,v in rates.items():
            code   = str(v)
            fhist  = fin.addhistory(k, logger = self.logger)
            h      = get_data(code, start = start, end = end)
            h.addCallbacks(fhist.update,fhist.errback)
        
    def get_rates(self, fin):
        '''
        return a dictionary of rate codes
        '''
        id     = fin.data_id
        rates = {}
        if id:
            rates['price'] = id.code
        return rates
        
    def dateobj(self):
        return self.__dateobj
    
    def __get_date(self):
        return self.__dateobj.dateonly
    date = property(fget = __get_date)
    
    def samedateas(self, r):
        return self.dateobj == r.dateobj()
    
    def __get_live(self):
        return self.__dateobj.live
    live = property(fget = __get_live)
        
    def calculate(self, inst, args = None):
        '''
        Perform calculation on given instrument.
        By default this methdo call the finins method precalculate
        @param inst: instance of finins
        @param args: input arguments  
        '''
        obj = inst.dbinstrument
        inst.precalculate(rate)
            
    def addrate(self, rte):
        if isinstance(rte,Rate):
            if self.samedateas(rte):
                if not self.__rates.has_key(rte.code):
                    self.__rates[rte.code] = rte
            else:
                raise DifferentDatesError
    
    
class sensitivity(object):
    
    def __init__(self):
        self.value  = 0
        self.deltas = {}
        self.gammas = {}
    
    
    
