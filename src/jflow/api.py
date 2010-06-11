
from jflow.db.finins import FinRoot, Fund, get_user
root = FinRoot()

get_object_id = root.get_object_id
get           = root.get   


def add_new_portfolio_view(id, user, name, description = '', default = False):
    '''Add new view to portfolio
    
        * **id** portfolio id
        * **user** user
        * **name** view name
        * *description* optional description of view
        * *default* if true the view is set as default
    '''
    user = get_user(user)
    p    = get(id)
    return p.add_new_view(user,name,description,default)



def get_portfolio_object(instance, user = None):
    '''Object to display'''
    if isinstance(instance,Fund):
        return root.default_view(instance,user)
    else:
        return instance    