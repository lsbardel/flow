'''Implementation of jflow.core.finins.Root methods for fetching
portfolio data.
'''
import logging
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import stdnet

from jflow.core import finins
from jflow.core.dates import yyyymmdd2date
from jflow.conf import settings
from jflow.utils.encoding import smart_str

from jflow.db.trade.models import FundHolder, Fund, Position, ManualTrade

from jflow.models import PortfolioHolder, Portfolio


class AuthenticationError(Exception):
    pass


def get_user(user, force = True):
    try:
        if isinstance(user,User):
            return user
        elif isinstance(user,Trader):
            return user.user
        else:
            return User.objects.get(username = str(user))
    except:
        if force:
            if not user:
                raise AuthenticationError('User not available')
            else:
                raise AuthenticationError('User %s not available' % user)
        else:
            return None


def get_portfolio_object(instance, user = None, dt = None):
    '''Get a portfolio object'''
    if isinstance(instance,Portfolio):
        return default_view(instance,user)
    elif isinstance(instance,Fund):
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
                positions = instance.positions.all(dt__lte = dt)
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
                        pass
                    
            
        #return get_portfolio_object(Portfolio.objects.get(id = instance),user)    


def default_view(fund, user):
    '''For a given fund and user get the default view. If not available, create a new one'''
    root = fund.root()
    if user and user.is_authenticated():
        view = UserViewDefault.objects.filter(user = user, view = root)
        if view:
            return view[0]
        views = root.views.filter()
        
        if not views:
            view = root.create_view('default',user)
            if not user:
                build_view(view)
            return view
    # No user
    else:
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
    
    
    
    