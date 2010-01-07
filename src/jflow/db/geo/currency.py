
from ccy import *

__all__ = ['currency',
           'currency_tuples',
           'currencydb',
           'ccypair',
           'currency_pair_tuples']
    

def currency_tuples():
    ccys = currencydb()
    cs = []
    for c in ccys.values():
        cs.append((c.id,c.id))
    return cs

def currency_pair_tuples():
    ccys = ccypairsdb()
    cs = []
    for c in ccys.values():
        cs.append((c.id,c.id))
    return cs

    

    