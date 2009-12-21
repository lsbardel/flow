from jflow.core.rates import objects
from jflow.core.rates import compositeCodeFactory

__all__ = ['fxfactory']


class fxfactory(compositeCodeFactory):
    '''
    Create a Cross FX composite rate
    '''
    def __init__(self, cache, code):
        codes = tuple(geo.currencydb().keys())
        super(fxfactory,self).__init__(cache, code, *codes)
        
    def populate(self):
        from jflow.db import geo
        cache = self.cache
        cdb = geo.currencydb()
        ccys = []
        for c in cdb:
            rh = cache.get_rate_holder(str(c.data))
            if rh:
                ccys.append(rh)
        self.hrates = ccys
        self.usd    = geo.currency('usd')
        
        
    def _make_composite(self, dte):
        return objects.crossfx(code = self.code(),
                               dte = dte,
                               holder = self.holder,
                               usd    = self.usd)
        