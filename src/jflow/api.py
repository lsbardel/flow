
def _api():
    from jflow.db import finins
    return finins


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