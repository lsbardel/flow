from django.core.exceptions import PermissionDenied

from models import Trader, FundHolder

def get_trader(user):
    if user.is_authenticated() and user.is_active:
        trader = user.traders.all()
        if trader:
            trader = trader[0]
        else:
            f,c = FundHolder.objects.get_or_create(code = 'NA')
            trader = Trader(fund_holder = f,
                            user = user)
            trader.save()
    else:
        raise PermissionDenied('User not authenticated or not active')
    return trader

def get_trader_or_none(user):
    try:
        return get_trader(user)
    except PermissionDenied:
        return None

def user_can_view_fund(user,fund):
    '''
    user is of type User
    fund is of type Fund
    '''
    from django.contrib.auth.models import User
    if isinstance(user,User):
        try:
            trader = user.trader_set.get()
        except:
            return False
    try:
        if trader.fund_holder == fund.fund_holder:
            return True
        else:
            return False
    except:
        return False
    
    
def get_user_servers(factory):
    from models import Trader
    from jflow.utils.servers import txconnsettings
    tr = Trader.objects.filter(server_active = True)
    serv = {}
    for t in tr:
        serv[str(t.user)] = txconnsettings(address = t.servername(),
                                           factory_class = factory,
                                           method = 'tcp') 
    return serv
    
