import datetime

from django.core.exceptions import *
from django.contrib.auth import authenticate

from jflow.core.dates import get_livedate
from jflow.db.trade.models import Position, FundHolder
from jflow.db.instdata.models import Future, FutureContract, InstDecomp
from jflow.utils.tx import runInThread, runInMainThread

from jflow.rates import get_cache, get_analysis

from unuk.core.jsonrpc.txweb import JSONRPC


cache = get_cache()
portfolio = FinRoot()



def flush_portfolio(code = None):
    from jflow.db.trade.aggregate import get_cache
    cache = get_cache()
    cache.flush(code)


def setup_dataserver():
    from jflow.core.timeseries import operators
    from jflow import rates
    from jflow import vendors
    
    # Get the rate cache handle
    cache = rates.get_cache()
    # set the live rate handle
    cache.vendorHandle = vendors.get_vendor
    
    from twisted.internet import reactor
    reactor.addSystemEventTrigger('before',
                                  'shutdown',
                                   cache.loaderpool.stop)


class jsonService(JSONRPC):
    '''JSONRPC server handler'''
    def __init__(self, **kwargs):
        setup_dataserver()
        super(jsonService,self).__init__(**kwargs)
        
    def jsonrpc_blbconnections(self):
        pass
    
    def jsonrpc_login(self, request, username, password):
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_active:
                return True
        return False
    
    def jsonrpc_history(self, request, code, start, end, period = 'd'):
        '''Retrive historical dataseries'''
        try:
            ts = get_analysis(code, start, end, period, json = True)
            if ts == None:
                self.err("while calling history: %s not available" % code)
                return []
            return ts.deferred
        except Exception, e:
            self.logger.error(e)
            return []
    
    def jsonrpc_numservers(self, request, code):
        '''Return the number of connected bloomberg servers'''
        from jflow.db.instdata.models import Vendor
        try:
            v = Vendor.objects.get(code = str(code))
            ci = v.interface()
            return len(ci.connected())
        except:
            return 0
        
    def jsonrpc_team(self, request, team, valdate):
        '''Request team data consisting of a list of aggregate positions across
        all funds.'''
        return portfolio.get_team_aggregate(team,valdate)
        
        
    @runInMainThread
    def jsonrpc_portfolio(self, request, viewid, valdate):
        '''
        Get a portfolio view
            viewid     Database id of view
            valdate    Valuation date
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.portfolioview(viewid, valdate, rjson = True)
    
    def jsonrpc_addfolder(self, request, viewid, valdate, code, parent_id):
        '''
        Add a new folder to a portfolio view
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.addfolder(viewid, valdate, code, parent_id, rjson = True)
    
    def jsonrpc_editfolder(self, request, viewid, valdate, data):
        '''
        Add a new folder to a portfolio view
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.editfolder(viewid, valdate, data, rjson = True)
    
    def jsonrpc_removePortfolioNode(self, request, viewid, valdate, id):
        '''
        remove a node from a portfolio view
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.removePortfolioNode(viewid, valdate, id, rjson = True)
        
    def jsonrpc_movePortfolioNode(self, request, viewid, valdate, id, target):
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.movePortfolioNode(viewid, valdate, id, target, rjson = True)
    
    def jsonrpc_marketRisk(self, request, viewid, valdate, id):
        '''
        Market risk for a position/portfolio/fund
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.marketRisk(viewid, valdate, id, rjson = True)
    
    def jsonrpc_aggregates(self, request, team, valdate):
        '''
        Aggregate team positions
        '''
        from jflow.db.trade.aggregate import get_cache
        cache = get_cache()
        return cache.aggregates(team, valdate, rjson = True)
        
    def jsonrpc_flushportfolio(self, request, code = None):
        flush_portfolio(code)
            
    def jsonrpc_flush(self, request):
        from jflow.rates import get_cache
        flush_portfolio()
        cache = get_cache()
        cache.clear()
        
    def jsonrpc_addinstrument(self, request, source, model, data):
        '''
        Add a new instrument to the database:
            source: string identifying where the data is coming from (bloomberg, web, etc..)
            model: instrument model
            data: dictionary with relevant data
        '''
        try:
            loader = get_loader(source,model,data)
            return loader.result
        except Exception, e:
            err = e.__class__('Failed adding instrument %s with data %s. %s' % (model,data,e))
            self.logger.err(err)
            raise e
    
    def jsonrpc_instruments(self, request, model):
        self.log('Getting list of %s' % model)
        objs = InstrumentCode.objects.formodel(model)
        ret  = []
        for o in objs:
            try:
                ret.append(o.tojson())
            except Exception, e:
                err = e.__class__('Failed in serializing instrument %s. %s' % (o,e))
                self.err(err)
        return ret
    
    def jsonrpc_composition(self, request, code, comp, tags):
        try:
            ic = InstrumentCode.objects.get(code = code)
            de = ic.instdecomp_set.all()
            if de:
                de = de[0]
            else:
                if comp:
                    de = InstDecomp(code = ic.code, instrument = ic)
                    de.save()
                else:
                    de = None
            if de:
                de.add(comp)
            id = ic.data_id
            if tags:
                tags = ' '.join(cleantag(tags))
                if id and id.tags != tags:
                    id.tags = tags
                    id.save()
            return "Done"
        except:
            return "Failed"
    
    def jsonrpc_loadmanualhistory(self, request, code, field, dt, value):
        #ic  = InstrumentCode.objects.get(code = code)
        id = getid(code)        
        dt  = get_livedate(dt).dateonly
        #try:
        field = str(field).upper()            
        #f = DataField.objects.get(code = field)
        #except:
        #    return "Field %s not available" % field
        vid = id.vendorid(field)
        if vid:
            f = DataField.objects.get(code = field)
            if f.format == 'numeric':
                model = MktData
                value = float(value)
            else:
                model = StringMktData
                value = str(value)
            v = model.objects.filter(vendor_id = vid, dt = dt, field = f)
            if v:
                v = v[0]
                v.mktvalue = value
            else:
                v = model(vendor_id = vid, dt = dt, field = f, mkt_value = value)
            v.save()
            return True
        else:
            return False
            
        