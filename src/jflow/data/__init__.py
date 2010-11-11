from stdnet import orm, ObjectNotFund 
from dynts.conf import settings as dynts_settings
from dynts.data import TimeSerieLoader, register
from jflow.db import dbapi

from jflow.data.blb import blb



def get_user_servers():
    raise StopIteration
    traders = Trader.objects.filter(server_active = True)
    for tr in traders:
        yield tr.user.username, tr.servername()


# Register Bloomberg data provider
register(blb(get_user_servers))


class DataIdCache(orm.StdModel):
    code = orm.AtomField(unique = True)



class jFlowLoader(TimeSerieLoader):
    
    def get_ticker(self, ticker):
        try:
            id = DataId.objects.get(code = ticker)
        except:
            return None
        
    def parse_symbol(self, symbol):
        ticker,field,provider = super(jFlowLoader,self).parse_symbol(symbol)
        try:
            id = dbapi.get_data(code = ticker)
        except ObjectNotFund:
            id = ticker
        return id,field,provider
        
    def preprocess(self, symbol, start, end, field, provider, logger, backend, **kwargs):
        try:
            intervals = id.intervals(start,end)
        except:
            intervals = ((start,end),)
        return self.preprocessdata(intervals)
        #if provider is None:
        #    provider = settings.DEFAULT_VENDOR_FOR_SITE
        
    def onresult(self, symbol, field, provider, result, logger, backend, **kwargs):
        '''We are going to store data into cache'''
        return result
    
    
    
dynts_settings.default_loader = jFlowLoader