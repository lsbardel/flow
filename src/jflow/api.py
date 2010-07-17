import ccy

def _api():
    from jflow.db import finins
    return finins

def _instapi():
    from jflow.db.instdata import api
    return api


def adddataid(code, curncy, country = None, **kwargs):
    if country is None:
        country = ccy.currency(curncy).default_country
    return _instapi().adddataid(code, curncy = curncy, country = country, **kwargs)

def instrument_types():
    '''A list of instrument types'''
    return ['equity','bond','future']

def add_new_portfolio_view(portfolio, user, name, description = '', default = False):
    '''Add new view to portfolio
    
        * **portfolio** portfolio or portfolio view to add new view to
        * **user** user owning the view
        * **name** view name
        * *description* optional description of view
        * *default* if true the view is set as default
    '''
    return _api().add_new_view(portfolio, user, name, description, default)



def get_portfolio_object(instance, user = None):
    '''Portfolio object to display.
    
        * **instance** could be a Fund instance, or a unique id
        * **user**
    '''
    return _api().get_portfolio_object(instance,user)