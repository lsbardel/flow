'''
Wrap jflow.core.rates to be used with django database modules
'''
from jflow.core import rates as RATES
from jflow.db.settings import MAX_RATE_LOADING_THREADS, LIVE_CALCULATION
from jflow.db.settings import LOGGING_VERBOSE, SERVER_LOGGER_MODULE
from jflow.db.geo import currency
from jflow.db.instdata.id import getid, get_vendor, getidobj
from jflow.db.utils import function_module
from jflow.utils.tx import ThreadPool

from twisted.python import log as twisted_log
import factory
import fields

__all__ = ['log',
           'get_cache',
           'getid',
           'get_rate',
           'get_history',
           'get_analysis',
           'get_value',
           'register_to_rates']

log = function_module(SERVER_LOGGER_MODULE, twisted_log)



def get_cache():
    '''
    override the get_cache form jflow.core.rates
    '''
    cache = RATES.get_cache()
    
    # If this is the first time we invoke the cache we set
    # the Factory handle and the currency handle
    if cache.factory == None:
        import codes
        cache.get_currency = currency
        cache.factory      = factory.Factory(cache, codes, getid)
        cache.get_field    = fields.get_field
        cache.get_vendor   = get_vendor
        cache.loopingCall  = None
        cache.log_verbose  = LOGGING_VERBOSE
        cache.logger       = log
        cache.livecalc     = LIVE_CALCULATION
        cache.loaderpool   = ThreadPool(name = "Rate loader pool",
                                        minthreads = 1,
                                        maxthreads = MAX_RATE_LOADING_THREADS)
    return cache

def load_factory(f):
    def wrapper(*args, **kwargs):
        cache = get_cache()
        return f(*args, **kwargs)
    return wrapper

get_rate           = load_factory(RATES.get_rate)
get_value          = load_factory(RATES.get_value)
get_history        = load_factory(RATES.get_history)
register_to_rates  = load_factory(RATES.register_to_rates)
get_analysis       = load_factory(RATES.get_analysis)


#def get_history(code, start, end, field = None):
#    hwrap = load_factory(RATES.get_history)
#    lo = hwrap(code, start, end, field)
#    return lo.get_result()
    
