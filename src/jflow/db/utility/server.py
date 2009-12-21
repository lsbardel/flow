from django.conf import settings
from models import Server

def userproxyserver(user):
    from jsonrpc.proxy import ServiceProxy
    #TODO    Create user specific servers
    
    debug = getattr(settings,'DEBUG_DATA_SERVER',False)
    
    if debug:
        url = getattr(settings,'JSONRPC_SERVER',None)
        if not url:
            raise ValueError, "No Debug JSONRPC_SERVER available" 
    else:
        se = Server.objects.all()
        if se:
            se = se[0]
        else:
            return None
        url = str(se.url)
        
    return ServiceProxy(url)
    