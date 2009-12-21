from txdjango import server


class txdjserver(server.txdjserver):
    '''
    Server for aggregating news feeds
    '''    
    def __init__(self, *args, **kwargs):
        # Setup environment
        self.aggregator = None
        super(txdjserver,self).__init__(*args, **kwargs)
        
    def _beforerun(self):
        '''
        override _beforerun
        '''
        from django.conf import settings
        from twisted.internet import reactor
        from twisted.python import log
        from jflow.servers.aggregator.news import news_aggregator
        map = self.map
        newsfreq = map['[global]'].get('newsfreq',None)
        self.aggregator = news_aggregator(log, callback_seconds = newsfreq)
        reactor.callLater(5,self.aggregator.run)