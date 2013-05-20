
import ccy

__all__ = ['country','country_map',
           'countryccy','countrycode','country_tuples']

ccy.set_country_map('GB','UK','United Kingdom')
ccy.set_new_country('WW','USD','World')
ccy.set_new_country('PX','AUD','Pacific Ex Japan')
ccy.set_new_country('PP','JPY','Pacific Rim')
ccy.set_new_country('LM','BRL','Latin America')

countrydb   = ccy.countries
country     = ccy.country
countryccy  = ccy.countryccy
country_map = ccy.country_map

def countrycode(code):
    cous = countrydb()
    code = ccy.country_map(code)
    if code:
        return code
    else:
        return ''

def country_tuples():
    global _countrytup
    return _countrytup
    
def _sort(x, y):
    if x[1] < y[1]:
        return -1
    else:
        return 1
    
_countrytup = sorted(countrydb().items(),_sort)