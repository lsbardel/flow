import json

from jflow.utils.tx import pb, runInThread

live_key = 'blb_live_feed'


def date2yyyymmdd(dte):
    return dte.day + 100*(dte.month + 100*dte.year)


class blbhistory(pb.tempref):
    
    def __init__(self, ticker, start, end, field):
        pb.tempref.__init__(self)
        self.ticker = ticker
        self.field  = field
        self.start  = date2yyyymmdd(start)
        self.end    = date2yyyymmdd(end)
        
    def getfield(self,field):
        pass
    
    def sendrequest(self, remote):
        f = int(self.field)
        remote.callRemote('history',self,self.ticker,self.start,self.end,f)
        
    def handleupdate(self, args):
        try:
            return json.loads(args)
        except Exception, e:
            pass
    
    
class blblive(pb.Referenceable):
    '''
    pb twisted bloomberg live client
    '''
    def __init__(self, rate, queue):
        self.rate  = rate
        self.queue = queue
        rate.livefeeds[live_key] = self
    
    def __get_ticker(self):
        try:
            return self.rate.vendorid.ticker
        except:
            return None
    ticker = property(fget = __get_ticker)
    
    def sendrequest(self, remote):
        ticker = self.ticker
        if ticker:
            remote.callRemote('registerlive',self,ticker)
        else:
            rate.livefeeds.pop('blb_live_feed')
    
    def remote_update(self, args):
        '''
        Remote update.
        The feed gets un update from the remote object
        '''
        self.queue.add(self.queue_update, args)
        
    def queue_update(self, args):
        try:
            arg = json.loads(args)
            self.rate.update(arg['body'])
        except:
            pass
    

