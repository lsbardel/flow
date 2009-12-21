

from equity import EquityPricer
from fund import FundPricer
from cash import CashPricer, FwdPricer, DepoPricer
from bond import BondPricer
from future import FuturePricer
from option import OptionPricer

__all__ = ['get_pricer']


_default = CashPricer()

_pricers = {'equity':   EquityPricer(),
            'cash':     CashPricer(),
            'fwd cash': FwdPricer(),
            'depo':     DepoPricer(),
            'fund':     FundPricer(),
            'bond':     BondPricer(),
            'etf':      FundPricer(),
            'future':   FuturePricer(),
            'warrant':  OptionPricer()}



def get_pricer(code):
    global _pricers, _default
    return _pricers.get(str(code).lower(),_default)

     
    