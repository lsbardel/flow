import logging
from datetime import date

from django.contrib.auth.models import User

import stdnet
import dynts

from jflow.conf import settings
from jflow.core import finins

from jflow.db.instdata.models import DataId
from jflow.db.trade.models import FundHolder, Fund, Position, ManualTrade, Trader
from jflow.db.portfolio.models import PortfolioHolder, Portfolio, FinIns
from jflow.db.portfolio.models import UserViewDefault, PortfolioView


class AuthenticationError(Exception):
    pass


def get_finins(symbol):
    symbol = symbol.upper()
    try:
        return FinIns.objects.get(code = symbol)
    except stdnet.ObjectNotFund:
        try:
            id = DataId.objects.get(code = symbol)
        except Exception, e:
            return None
        fi = FinIns(id = id.id,
                    code = id.code,
                    country = id.country,
                    curncy = id.curncy,
                    firm_code = id.firm_code,
                    type = id.type,
                    metadata = id.metadata())
        return fi.save()
        

def get_user(user, force = True):
    if not user:
        if force:
            raise AuthenticationError('User not available')
        return None
    
    try:
        if isinstance(user,User):
            return user
        elif isinstance(user,Trader):
            return user.user
        else:
            return User.objects.get(username = str(user))
    except:
        if force:
            raise AuthenticationError('User %s not available' % user)
        else:
            return None


def get_portfolio_object(instance, user = None, dt = None, name = None):
    '''Get a portfolio object'''
    if isinstance(instance,Fund):
        instance = create_portfolio_from_fund(instance, dt)
    if isinstance(instance,Portfolio):
        return default_view(instance,user,name)


def default_view(portfolio, user, name):
    '''For a given fund and user get the default view. If not available, create a new one'''
    root = portfolio.root()
    user = get_user(user,False)
    if user and user.is_authenticated():
        username = user.username
    else:
        username = None
        
    if name:
        view = PortfolioView.objects.filter(user = username, name = name, portfolio = portfolio)
        if view:
            return view[0]
    
    if username:
        view = UserViewDefault.objects.filter(user = username, view = root)
        if view:
            return view[0]
    
    # No user view
    uviews = root.views.filter(name = 'default', user = None)
    if uviews:
        return uviews[0]
    else:
        view = root.create_view('default')
        return build_new_view(view)
    


def build_new_view(view, portfolio = None):
    '''Build a new view based on position instrument type'''
    portfolio = portfolio or view.portfolio
    children = portfolio.children()
    if children:
        for child in children:
            build_new_view(view, child)
    else:
        for pos in portfolio.positions.all():
            type   = pos.type
            folder = view.folders.filter(name = type)
            if folder:
                folder = folder[0]
            else:
                folder = view.addfolder(name = type)
            folder.positions.add(pos)
            folder.save()
            
    return view


def build_view(view):
    '''Build a view based on position instrument type'''
    positions = dict((p.id,p) for p in view.portfolio.positions.all())
    children = view.children.all()
    # First loop over children
    for child in children:
        for pp in child.portfolio_positions.all():
            pos = positions.pop(pp.position.id,None)
            if not pos:
                pp.delete()
    for pos in positions.itervalues():
        type = pos.instrument.type
        child = view.children.filter(name = type)
        if child:
            child = [0]
        else:
            child = view.addNewFolder(name = type)
        child.addposition(pos)
    return view
    
    
########################################################################################    
# INTERNAL FUNCTIONS


def create_portfolio_from_fund(instance, dt):
    '''Create a portfolio from a fund instance.'''
    try:
        holder = PortfolioHolder.objects.get(name = instance.code)
    except stdnet.ObjectNotFund:
        holder = PortfolioHolder(name  = instance.code,
                                 group = instance.fund_holder.code,
                                 description = instance.description,
                                 ccy   = instance.curncy).save()
    dt = dt or date.today()
    portfolio = Portfolio.objects.filter(holder = holder, dt = dt)
    if not portfolio.count():
        children = instance.children.all()
        if children:
            for child in children:
                pass
        else:
            positions = instance.position_set.filter(dt__lte = dt)
            if positions.count():
                latest_date = positions.latest().dt
                if latest_date < dt:
                    portfolio = Portfolio.objects.filter(holder = holder, dt = latest_date)
                else:
                    latest_date = dt
                if not portfolio.count():
                    portfolio = Portfolio(holder = holder, dt = latest_date).save()
                    positions = positions.filter(dt = latest_date)
                    for position in positions:
                        did = position.dataid
                        try:
                            fins = FinIns.objects.get(name = did.code)
                        except stdnet.ObjectNotFund:
                            inst = did.instrument
                            fins = FinIns(name = did.code,
                                          country = did.country,
                                          ccy  = did.curncy,
                                          type = inst._meta.module_name).save()
                        portfolio.addnewposition(fins, position.size, position.value)
                else:
                    portfolio = portfolio[0]
    else:
        portfolio = portfolio[0]
    return portfolio
