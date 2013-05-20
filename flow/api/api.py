###########################################################
# JFLOW PYTHON API
###########################################################
import ccy
import jflow
import dynts
import jflow.data
from jflow.db.api import *

class holder:
    controller = None
        
_controller = holder()

def get_controller():
    global _controller
    return _controller.controller

def set_controller(controller):
    global _controller
    _controller.controller = controller
    
    

###################################################################################
# API START

def get_version():
    '''jflow version tuple'''
    return jflow.get_version()


def adddataid(code, curncy, country = None, **kwargs):
    '''Add new data id to database'''
    if country is None:
        country = ccy.currency(curncy).default_country
    return _api.adddataid(code, curncy = curncy, country = country, **kwargs)


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
    return _api.add_new_view(portfolio, user, name, description, default)


def get_portfolio_object(instance, user = None):
    '''Portfolio object to display.
    
        * **instance** could be a Fund instance, or a fund unique id.
        * **user** optional user
    '''
    return _api.get_portfolio_object(instance,user)


def create_user_view(instance, name, user, default = False):
    '''Create a new Portfolio view for a user.
    
    * *instance* a Fund a Portfolio or PortfolioView instance
    * *name* name of the new view
    * *user* user owner of the view
    * *default* if set to True, it will be the default view of the user for the portfolio.
    '''
    view = _api.get_portfolio_object(instance, user, name = name)
    build = False
    if view.name != name or not view.user:
        build = True
        root = view.portfolio
        view = root.create_view(name,user)
    defaults = _api.UserViewDefault.objects.filter(user = view.user, portfolio = view.portfolio)
    if default or not defaults:
        defaults.delete()
        _api.UserViewDefault(user = view.user, portfolio = view.portfolio, view = view).save()
    if build:
        return _api.build_new_view(view)
    else:
        return view


def get_analysis(code = None, start = None, end = None, format = None, **kwargs):
    '''Econometric analysis'''
    res = dynts.evaluate(code, start = start, end = end)
    if format:
        return res.dump(format = format)
    else:
        return res
    