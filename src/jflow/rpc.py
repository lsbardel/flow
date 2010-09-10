#
#    JSON RPC API
#
from unuk.core.jsonrpc import JSONRPC
from unuk.contrib import tasks


from jflow import pyapi


def get_controller():
    c = pyapi.get_controller()
    if not c:
        c = tasks.Controller()
        pyapi.set_controller(c)
    return c


class JFlowRPC(JSONRPC):
    
    def __init__(self, *args, **kwargs):
        self.controller = get_controller()
        super(JSONRPC,self).__init__(*args, **kwargs)
    
    def jsonrpc_version(self, request, full = False):
        pyapi.get_version(full)
    
    def jsonrpc_history(self, request, code, start, end, period = 'd'):
        '''Retrive historical dataseries'''
        try:
            ts = pyapi.get_analysis(code, start, end, period, json = True)
            if ts == None:
                self.err("while calling history: %s not available" % code)
                return []
            return ts.deferred
        except Exception, e:
            self.logger.error(e)
            return []
    