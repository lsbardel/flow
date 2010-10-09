from bloomberg.utils.servers import txconnsettings
from bloomberg.utils.tx import ConnectionPool, pb
from bloomberg.pb.queue import SingleThreadQueueUpdate
import client


class BlbConnFactory(pb.PbReconnectingClientFactory):
    
    def __init__(self, *args, **kwargs):
        pb.PbReconnectingClientFactory.__init__(self, *args, **kwargs)
        
    def clenup(self):
        '''
        Clear the rate cache from live rates
        '''
        from jflow import rates
        cache = rates.get_cache()
        cache.clearlive(client.live_key)



class BloombergPool(ConnectionPool):
    '''
    Bloomberg Connection Manager.
    It mainatins a pool of bloomberg connections
    '''
    def __init__(self,servers,*args,**kwargs):
        self._servers = servers
        super(BloombergPool,self).__init__(*args,**kwargs)
        self.livethread = SingleThreadQueueUpdate()
    
    def get_servers(self):
        serv = {}
        for name,address in self._servers():
            serv[name] = txconnsettings(address = t.servername(),
                                        factory_class = BlbConnFactory,
                                        method = 'tcp')
        return serv
    
    def history(self, ticker, startdate, enddate, field):
        server = self.get()
        if server:
            blbh = client.blbhistory(ticker, startdate, enddate, field)
            d = server.getRootObject()
            d.addCallback(blbh.sendrequest)
            return blbh.deferred
        else:
            return None
        
    def registerlive(self, rate):
        server = self.get()
        if server:
            blbl = client.blblive(rate, self.livethread)
            d = server.getRootObject()
            d.addCallback(blbl.sendrequest)