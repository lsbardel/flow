from stdnet import orm 
from dynts.conf import settings as dynts_settings
from dynts.data import TimeSerieLoader, register

from jflow.conf import settings
from jflow.db.instdata.models import DataId
from jflow.db.trade.models import Trader

from jflow.data.blb import blb



def get_user_servers():
    raise StopIteration
    traders = Trader.objects.filter(server_active = True)
    for tr in traders:
        yield tr.user.username, tr.servername()


register(blb(get_user_servers))


class DataIdCache(orm.StdModel):
    code = orm.AtomField(unique = True)



class jFlowLoader(TimeSerieLoader):
    
    def get_id(self, ticker):
        try:
            id = DataId.objects.get(code = ticker)
        except:
            return None
        
    def preprocess(self, ticker, start, end, field, provider, logger, backend, **kwargs):
        try:
            id = DatIdCache.objects.get(code = ticker)
        except:
            id = self.get_id(ticker)
        if not id:
            return super(jFlowLoader,self).preprocess(ticker, start, end, field, provider, logger, backend, **kwargs)
        if provider is None:
            provider = settings.DEFAULT_VENDOR_FOR_SITE
        return id
    
    
    
dynts_settings.default_loader = jFlowLoader