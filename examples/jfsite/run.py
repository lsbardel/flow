import sys
import os
from optparse import OptionParser

def makeoptions():
   parser = OptionParser()
   parser.add_option("-d", "--debug",
                     action="store_true",
                     dest="debug",
                     default=False,
                     help="Run server in debug mode")
   parser.add_option("-r", "--rpc",
                     action="store_true",
                     dest="rpcserver",
                     default=False,
                     help="Run rpc server only")
   parser.add_option("-w", "--web",
                       action="store_true",
                       dest="webserver",
                       default=False,
                       help="Run web server only")
   parser.add_option("-p", "--port",
                     type = int,
                     action="store",
                     dest="port",
                     default=0,
                     help="Starting port where running servers")
   return parser


def run(settings = None):
    from environment import local_dir
    options, args = makeoptions().parse_args()
    if not settings:
        if options.debug:
            setting_module = 'debug'
        else:
            setting_module = 'release'
        settings = 'jfsite.allsettings.%s' % setting_module
    import jflow
    jflow.set_settings(settings)
    from jflow.conf import settings
    from jflow.db.portfolio.admin import register
    register()
   
    from unuk.contrib.txweb import jsonrpc, djangoapp, start
    from unuk.utils import get_logger

    rpcport = options.port or settings.RPC_SERVER_PORT
    webport = rpcport+1
    webserver, rpcserver = None,None
    try:
        if options.rpcserver:
            from jflow.rpc import JFlowRPC
            rpcserver = jsonrpc.ApplicationServer(JFlowRPC, port = rpcport)
            rpcserver.service.logger.info('Listening on port %s'% rpcport)
        if options.webserver:
            webserver = djangoapp.ApplicationServer(local_dir, port = webport)
            webserver.service.logger.info('Listening on port %s'% webport)
        
        if not (webserver or rpcserver):
            rpcserver = jsonrpc.ApplicationServer(JFlowRPC, port = rpcport)
            webserver = djangoapp.ApplicationServer(local_dir, port = webport)
    except Exception, e:
        print(e)
        exit()
    
    start()

if __name__ == '__main__':
    run()    