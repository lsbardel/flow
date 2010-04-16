'''
Wrap jflow.core.rates to be used with django database modules
in jflow.db
This guarantees the separtion from jflow.core and jflow.db
'''
from jflow.conf import settings
from jflow.core import rates as RATES
from jflow.db.geo import currency
from jflow.db.utils import function_module
from jflow.db.instdata.id import get_id, get_vendor, get_field
import factory

__all__ = ['get_cache',
           'get_id',
           'get_rate',
           'get_history',
           'get_analysis',
           'get_value',
           'register_to_rates']

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
        cache.factory      = factory.Factory(codes, get_id)
        cache.get_field    = get_field
        cache.get_vendor   = get_vendor
    return cache

def load_factory(f):
    def wrapper(*args, **kwargs):
        get_cache()
        return f(*args, **kwargs)
    return wrapper

get_rate           = load_factory(RATES.get_rate)
get_value          = load_factory(RATES.get_value)
get_history        = load_factory(RATES.get_history)
register_to_rates  = load_factory(RATES.register_to_rates)
get_analysis       = load_factory(RATES.get_analysis)
