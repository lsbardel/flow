from txdjango import server

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
    

class txdjserver(server.txdjserver):
    
    def __init__(self, *args, **kwargs):
        super(txdjserver,self).__init__(*args, **kwargs)
        setup_dataserver()