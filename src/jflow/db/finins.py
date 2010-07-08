'''Implementation of jflow.core.finins.Root methods for fetching
portfolio data.
'''
import logging

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from jflow.core import finins
from jflow.core.dates import yyyymmdd2date
from jflow.conf import settings
from jflow.utils.encoding import smart_str

from jflow.db.trade.models import FundHolder, Fund, Position, ManualTrade
from jflow.db.portfolio.models import Portfolio


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


def get_portfolio_object(instance, user = None):
    if isinstance(instance,Portfolio):
        if instance.holder:
            return instance
        else:
            return default_view(instance,user)
    else:
        return get_portfolio_object(Portfolio.objects.get(id = instance),user)    


def default_view(fund, user):
    '''For a given fund and user get the default view. If not available, create a new one'''
    root = fund.root()
    if user and user.is_authenticated():
        view = UserViewDefault.objects.filter(user = user, view = root)
        if view:
            return view[0]
    views = Portfolio.objects.filter(holder = root)
    if not views:
        view = root.create_view('default',user)
        if not user:
            build_view(view)
        return view
    else:
        if user.is_authenticated():
            uviews = views.filter(user = user)
            if uviews:
                return uview[0]
        uviews = views.filter(name = 'default')
        if uviews:
            return uviews[0]
        else:
            return views[0]


def build_view(view):
    '''Build a view based on position instrument type'''
    positions = dict((p.id,p) for p in view.holder.positions.all())
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
    
    
    
    