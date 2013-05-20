from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from jflow.core.finins import Portfolio as FinInsPortfolio
from jflow.db.tools import livepositions
from jflow import get_full_user, create_user_portfolio_view

from models import *


def get_liveposition(dt, fund = None):
    pos = Position.objects.filter(Q(open_date__lte = dt),
                                  Q(close_date__gt = dt) | Q(close_date__isnull=True))
    if fund:
        return pos.filter(fund = fund)
    else:
        return pos    


def displays():
    displays = PortfolioDisplay.objects.all()
    jdisp = []
    for d in displays:
        elems = d.portfoliodisplaycomponent_set.all()
        els = []
        for el in elems:
            eu   = el.element
            code = eu.code
            els.append({'name':  code,
                        'label': eu.name,
                        'description':eu.description,
                        'formatter': eu.formatter,
                        'sortable':  eu.sortable})
        jd = {'code': d.code,
              'name': d.name,
              'description': d.description,
              'elems': els}
        jdisp.append(jd)
    return jdisp


def createportfolio0(dt, user):
    '''
    Obsolete, not used
    '''
    user     = get_full_user(user)
    team     = user.fund_holder
    delems   = list(PortfolioDisplayElement.objects.all())
    
    if team == None:
        root = Portfolio(code = 'root')
        fholders = FundHolder.objects.all()
        fflist   = []
        for holder in fholders:
            fflist.append(root.add(Portfolio(dbobj = holder,
                                             display = delems)))
    else:
        root   = Portfolio(dbobj = team,
                           display = delems)
        fflist = [root]
    
    # Loop over fund holders
    for fholder in fflist:
        funds   = fholder.dbobj.fund_set.all()
        for f in funds:
            po  = fholder.add(Portfolio(dbobj = f,
                                        display = delems))
            positions = Position.objects.filter(fund = f, open_date__lte = dt)
            
            # Loop over Positions
            for pos in positions:
                p = po.add(pos.getposition(dt))
                if p:
                    p.display = delems
    return jportfolio(data = root, displays = displays())


def get_port_id(obj):
    opt = obj._meta
    ct = ContentType.objects.get_for_model(obj)
    return '%s_%s' % (ct.id,obj.id)

def get_object_from_id(id):
    try:
        ids = str(id).split('_')
        ct = ContentType.objects.get_for_id(int(ids[0]))
        return ct.get_object_for_this_type(id = int(ids[1]))
    except:
        return None
    
    
def _add_position(parent,pos,delems,dt):
    '''
    Add position to portfolio
    '''
    p = parent.add(pos.getposition(dt))
    p.id = get_port_id(pos)
    if p:
        p.display = delems


def add_to_portfolio(bas, port, delems, dt):
    parent = bas.add(FinInsPortfolio(dbobj = port, id = get_port_id(port)))
    
    # Get the subportfolios if they exists
    sub_ports = port.portfolio_set.all()
    for child in sub_ports:
        add_to_portfolio(parent, child, delems, dt)

    # Add positions if available
    positions = port.position.filter(open_date__lte = dt, close_date = None)
    for pos in positions:
        _add_position(parent,pos,delems,dt)


def createportfolio(dt, fund, view):
    '''
    Create the portfolio JSON object for a given fund
    '''
    positions = livepositions(dt, fund = fund)
    
    delems = list(PortfolioDisplayElement.objects.all())
    root   = FinInsPortfolio(dbobj = fund)
    
    # Get the subportfolios
    subs = view.portfolio_set.filter(parent = None)
    for s in subs:
        add_to_portfolio(root, s, delems, dt)
        
    for pos in positions:
        if not pos.portfolio_set.filter(view = view).count():
            _add_position(root,pos,delems,dt)
            
    return jportfolio(data = root, displays = displays())



def get_livepositions(dt, fund = None):
    '''
    Create the list of live positions at date dt
    '''
    from jflow.db.tools.positions import livepositions
    pos = livepositions(dt,fund=fund)
    plist = []
    for p in pos:
        ip = p.getposition(dt)
        plist.append(ip)
    
    return plist
    
    
    

