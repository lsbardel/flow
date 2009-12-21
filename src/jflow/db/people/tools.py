

def get_full_user1(user):
    from django.contrib.auth.models import User, AnonymousUser    
    if not isinstance(user,User):
        try:
            user = User.objects.get(username = str(user))
        except:
            pass
            
    if not isinstance(user,User):
        user = AnonymousUser()
        user.preference = None
    else:
        try:
            user.preference = user.get_profile()
        except:
            user.preference = None
    
    return user

def get_or_create_pref(user = None, trader = None):
    from jflow.db.trade.models import Trader, Fund
    from models import PeopleData
    if user:
        try:
            td = Trader.objects.get(user = user)
        except:
            return None
    elif trader:
        td = trader
    else:
        return None
    try:
        return PeopleData.objects.get(trader = td)
    except:
        return create_people(td) 


def get_full_user(user):
    user = get_full_user1(user)
    if user.preference:
        people = get_or_create_pref(trader = user.preference)
        return people
    else:
        return user

    
def create_people(trader):
    from models import PeopleData
    funds = trader.fund_holder.fund_set.all()
    if funds:
        fund = funds[0]
        p = PeopleData(trader = trader, default_fund = fund)
        p.save()
        return p
    else:
        return None
    
def create_user_portfolio_view(view,user):
    from jflow.db.people.models import UserPortfolioView
    from jflow import user_can_view_fund

    try:
        pv = view.userportfolioview
        pv.default = view.default
    except:
        pv = UserPortfolioView(view = view, user = user, default = view.default)
    pv.save()
    
    uviews = user.userportfolioview_set.all()
    if pv.default or uviews.filter(default=True).count() == 0:
        for u in uviews:
            u.default = False
            u.save()
        pv.default = True
        pv.save()
    return pv

def get_user_portfolio_view(fund,user):
    from jflow.db.trade.models import PortfolioView
    from jflow import user_can_view_fund
    
    if user_can_view_fund(user,fund):
        views = user.userportfolioview_set.filter(view__fund = fund)
        dview = views.filter(default = True)
        if dview.count():
            return dview[0]
        elif views.count():
            view = views[0]
            view.default = True
            view.save()
            return view
        else:
            view = PortfolioView(fund = fund, default = True, name = '%s default' % user)
            view.save()
            return create_user_portfolio_view(view,user)
    else:
        return None
        

def get_all_portfolio_for_fund(fund):
    from jflow.db.trade.models import PortfolioView
    return PortfolioView.objects.filter(fund = fund)

def get_all_userportfolio_for_fund(fund):
    from jflow.db.people.models import UserPortfolioView
    return UserPortfolioView.objects.filter(view__fund = fund)


def create_user_preferences(user, team):
    from jflow.db.trade.models import Trader
    t = Trader(user = user, fund_holder = team)
    t.save()
    return create_people(t)