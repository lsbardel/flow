from twisted.internet import reactor

from joinfeed import utils

from jflow.utils.tx import runInThread

DEFAULT_CALLBACK_SECONDS = 5*60


class news_aggregator(object):
    
    def __init__(self, log, callback_seconds = None):
        cs = callback_seconds or DEFAULT_CALLBACK_SECONDS
        try:
            cs = float(cs)
        except:
            cs = DEFAULT_CALLBACK_SECONDS
        self.cs  = max(cs,0.1)
        self.log = log
    
    def run(self):
        self.__handle()
        
    #@runInThread
    def __handle(self):
        handle_aggregate(log = self.log)
        reactor.callLater(self.cs, self.__handle)
        
        
        
def handle_aggregate(log = None, force = False):
    posts = utils.update(log = log, force = force)
    if not posts:
        return
    if log:
        N = len(posts)
        p = ''
        if N > 1:
            p = 's'
        log.msg("Aggregating %s new post%s" % (N,p))
    for p in posts:
        handle_post(p)
        
def handle_post(post):
    pass
    
    
    
    
    
    