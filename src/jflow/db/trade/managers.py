import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q
from django.db import models

from jflow.utils.anyjson import json

ROUNDING   = 4
MAX_DIGITS = 18

#Positions status flags_________________________
POSITION_STATUS_DUMMY       = 0
POSITION_STATUS_SYNCRONIZED = 1
POSITION_STATUS_MANUAL      = 2
INITIAL_FIELDS = 'name,description,ccy,size'
#POSITION_STATUS_TRADE_TRACK = 3
#_______________________________________________



position_status_choice = (
                          (POSITION_STATUS_DUMMY,'Dummy'),
                          (POSITION_STATUS_SYNCRONIZED,'Syncronized'),
                          (POSITION_STATUS_MANUAL,'Manuall'),
                          #(POSITION_STATUS_TRADE_TRACK.'TRADE')
                          )

class aggposition(list):
    
    def __init__(self, ic, dt = None):
        self.instrumentCode = ic
        self.dt   = dt or datetime.date.today()
        self.size = 0
        
    def append(self, p):
        pv = p.first_at_or_before(self.dt)
        self.size += pv.size
        super(aggposition,self).append({'position': p,'history': pv})


class TraderManager(models.Manager):
    
    def create_superuser(self, username, email, password, team):
        from models import FundHolder
        u = User.objects.create_superuser(username, email, password)
        if not isinstance(team,FundHolder):
            team = FundHolder.objects.get(code = team)
        t = self.model(user = u, fund_holder = team)
        t.save()
        return t    


class FundManager(models.Manager):
    
    def parents(self, holder):
        return self.filter(fund_holder = holder, parent__isnull=True)
    
    def subfunds(self, holder):
        qs = self.filter(fund_holder = holder)
        object_ids = []
        for f in qs:
            if not f.fund_set.all():
                object_ids.append(f.id)
        return self.filter(pk__in=object_ids)
        

class PortfolioViewManager(models.Manager):
    
    def get_default(self, user, fund):
        dv = UserViewDefault.objects.filter(user = user, view__fund = fund)
        if dv.count() == 1:
            return dv[0].view
        elif dv.count() == 0:
            return None
        else:
            raise ValueError('%s seems to have more than one default view for fund %s' % (user,fund))
        
    def get_last_modified(self):
        try:
            p = self.latest('last_modified')
            return p.last_modified
        except:
            return datetime.datetime.min
        
        
class CustodyAccountManager(models.Manager):

    def get_for_fund(self, fund):
        custodian = self.filter(fund = fund)
        if custodian.count():
            custodian = custodian[0]
        else:
            custodian = self.model(code = '%s_CustAcc' % fund.code,
                                   name = '',
                                   fund = fund)
            custodian.save()
        return custodian


class OldPositionManager(models.Manager):
        
    def status_filter(self, status):
        if str(status).lower() == 'all':
            return self.filter()
        
        status_values = list(dict(position_status_choice))
        try:
            status = list(status)
        except:
            status = [status]
        cstatus = []
        for s in status:
            try:
                si = int(s)
            except:
                si = POSITION_STATUS_SYNCRONIZED
            if si not in cstatus:
                cstatus.append(si)
        s = cstatus.pop(0)
        du = Q(status = s)
        for s in cstatus:
            du = du & Q(status = s)
        return self.filter(du)    
    
    def status_date_filter(self, dt = None, status = POSITION_STATUS_SYNCRONIZED):
        dt = dt or datetime.date.today()
        qs = self.status_filter(status)
        return qs.filter(Q(open_date__lte = dt),
                         Q(close_date__gt = dt) | Q(close_date__isnull=True))
    
    def positions_for_fund(self, fund = None, dt = None, status = POSITION_STATUS_SYNCRONIZED):
        qs    = self.status_date_filter(dt = dt, status = status)
        if not fund:
            return qs
        else:
            return qs.filter(fund = fund)
        
    def positions_for_team(self, team = None, dt = None, status = POSITION_STATUS_SYNCRONIZED):
        qs    = self.status_date_filter(dt = dt, status = status)
        if not team:
            return qs        
        else:
            return qs.filter(fund__fund_holder = team)
        #qn = connection.ops.quote_name
        #fq    = """
        #    SELECT %(fund_portfolio)s.fund_id
        #    FROM %(fund_portfolio)s, %(fund_parent)s
        #    WHERE %(fund_parent)s.fund_holder_id = %(team_id)s
        #    AND  %(fund_portfolio)s.parent_id = %(fund_parent)s.id
        #    """ % {
        #    'fund_portfolio': qn(FundPortfolio._meta.db_table),
        #    'fund_parent': qn(ParentFund._meta.db_table),
        #    'team_id': team.pk
        #    }
        #WHERE %(fund_portfolio)s.parent.fund_holder_id = %(team_id)s
        #AND %(fund_portfolio)s.fund_id = %(model)s.fund_id
        #cursor = connection.cursor()
        #cursor.execute(fq)
        #fund_ids = [row[0] for row in cursor.fetchall()]
        #return qs.filter(fund__in = fund_ids)
        
    def aggregate_positions(self, team = None, dt = None, dummy = False):
        '''
        Return a dictionary contains aggregated positions
        for a given team and a given date
        '''
        qs = self.positions_for_team(team = team, dt = dt, dummy = dummy)
        pd = {}
        for p in qs:
            ic   = p.instrumentCode
            code = ic.code
            agg = pd.get(code,None)
            if not agg:
                agg = aggposition(ic,dt)
                pd[code] = agg
            agg.append(p)
        return pd
    
    def get_or_create_position(self, fund, open_date, ic,
                               custodian = None, status = POSITION_STATUS_SYNCRONIZED):
        '''
        Utility method for retriving a position given
            fund
            open_date
            instrumentCode
            custodian
            status
            
        If an open position for open_date is not found a new position is constructed
        '''
        from jflow.db.trade.models import CustodyAccount as CA
        c = custodian or CA.objects.get_for_fund(fund)
        postn = self.filter(Q(instrumentCode = ic),
                            Q(fund           = fund),
                            Q(custodian      = c),
                            Q(status         = status),
                            Q(open_date__lte = open_date),
                            Q(close_date__gt = open_date) | Q(close_date__isnull=True))
        
        if postn.count() == 0:
            # Is new position
            postn = self.model(instrumentCode = ic,
                               fund           = fund,
                               custodian      = c,
                               open_date      = open_date,
                               status         = status)
            postn.save()
        elif postn.count() == 1:
            # Is existing position
            postn = postn[0]
        else:
            raise ValueError, "There are %s conflicting positions %s in %s" % (ic,fund)
        
        return postn
    
    def clear_from_date(self, dt):
        '''
        delete all positions and histories opened after given date
        '''
        qs = self.filter(Q(open_date__gte = dt) | Q(close_date__gte = dt)) 
        N = qs.count()
        qs.delete()
        return N    
    



class PositionManager(models.Manager):
    '''
    Position manager
    '''
    def status_date_filter(self, dt = None, status = POSITION_STATUS_SYNCRONIZED, **kwargs):
        '''
        This query needs to be cached in an efficient manner
        '''
        dt = dt or datetime.date.today()
        base = self.filter(status = status, dt__lte = dt, **kwargs)
        if base:
            # get the latest position data and filter
            pos = base.latest()
            return base.filter(dt = pos.dt)
        else:
            return base
        
    def for_fund(self, fund, **kwargs):
        return self.status_date_filter(fund = fund, **kwargs)
    
    def for_team(self, team, **kwargs):
        return self.status_date_filter(fund__fund_holder = team, **kwargs)
    
    def predate(self, position, dt):
        return self.filter(position = position, dt__lte = dt)
    
    def postdate(self, position, dt):
        return self.filter(position = position, dt__gt = dt)
    
    def addnew(self,
               fund,
               dt,
               instrument,
               status      = POSITION_STATUS_SYNCRONIZED,
               size        = 0,
               value       = 0,
               dirty_value = None):
        '''
        Add a new position history to databse
            fund              Fund instance
            dt                relevant date
            instrument        instrumentCode instance
            status            position status
            
        ''' 
        po = PO.objects.get_or_create_position(fund,
                                               dt,
                                               instrument,
                                               status = status)
        preh  = self.predate(po,dt)
        if preh:
            preh = preh[0]
            if preh.dt < dt:
                # Create a new history point
                preh = self.model(position = po, dt = dt)
        else:
            preh = self.model(position = po, dt = dt)
        
        dirty_value       = dirty_value or value 
        preh.size        += Decimal(str(size))
        preh.value       += float(value)
        preh.dirty_value += float(dirty_value)
        preh.save()
        
        # Now check for post date positions
        posth  = self.postdate(po,dt)
        for p in posth:
            p.size  += size
            p.value += value
        
        return preh
    
    def add_from_size_and_price(self,
                                fund,
                                dt,
                                instrument,
                                status = POSITION_STATUS_SYNCRONIZED,
                                size   = 0,
                                price  = 0):
        inst = instrument.instrument()
        fins = inst.make_position()
        price = float(str(price))
        size  = float(str(size))
        fins.mktprice = price
        value = fins.notional(size = size)
        return self.addnew(fund, dt, instrument,
                           status=status,
                           size=size,
                           value = value,
                           dirty_value = value)
        
    def clear_from_date(self, dt):
        qs = self.filter(dt__gte = dt)
        N  = qs.count()
        qs.delete()
        return N
    

class ManualTradeManager(models.Manager):
    
    def status_date_filter(self, dt = None, **kwargs):
        '''This query needs to be cached in an efficient manner
        '''
        dt = dt or datetime.date.today()
        base = self.filter(open_date__lte = dt, **kwargs)
        return base.filter(Q(close_date__gt = dt) | Q(close_date__isnull=True))
        
    def for_team(self, team, dt = None):
        return self.status_date_filter(dt = dt, fund__fund_holder = team)
    
    def for_fund(self, fund, dt = None):
        return self.status_date_filter(dt = dt, fund = fund)



    

class PortfolioDisplayManager(models.Manager):
    
    def create_default(self, user = None):
        m = self.model(name = 'default',
                       fields = INITIAL_FIELDS,
                       user = user)
        m.save()
        
    def for_user(self, user = None):
        if isinstance(user,User):
            ps = self.filter(user = user)
            if not ps:
                self.create_default(user)
                return self.filter(user = user)
            else:
                return ps
        else:
            ps = self.filter(user = None)
            if not ps:
                self.create_default()
                return self.filter(user = None)
            else:
                return ps
    
    def dict_user(self, user):
        ps = self.for_user(user)
        d = dict((d.name,d.fieldlist()) for d in ps.order_by('name'))
        return d
    