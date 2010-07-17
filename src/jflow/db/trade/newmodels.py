#
#    Requires:
#        - jflow.db.instdata
#        - ccy.basket
#
#
#
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import capfirst

from jflow.db.trade import managers
from jflow.db import geo
from jflow.db.instdata.fields import slugify, SlugCode


fund_choices = (('fund','fund'),
                ('benchmark','benchmark'),
                ('custom','custom'))


class TimeStamp(models.Model):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True


class FundHolder(models.Model):
    code         = SlugCode(unique=True, max_length=10)
    description  = models.CharField(max_length=255, blank = True)
    fund_manager = models.BooleanField(default = False)
    
    class Meta:
        verbose_name = 'team'
        ordering     = ('code',)
    
    def __unicode__(self):
        return u'%s' % self.code


class Fund(models.Model):
    code            = SlugCode(unique=True, max_length=10)
    firm_code       = models.CharField(unique=True, max_length=50)
    description     = models.CharField(max_length=255, blank = True)
    fund_holder     = models.ForeignKey(FundHolder, verbose_name = 'team', related_name = 'funds')
    curncy          = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    parent          = models.ForeignKey('self', null = True, blank = True, related_name = 'children')
    dataid          = models.ForeignKey('instdata.DataId',
                                        blank = True,
                                        null = True,
                                        related_name = 'dataid')
    # New stuff
    type            = models.CharField(choices = fund_choices,
                                       max_length = 32,
                                       blank = True,
                                       default = 'fund')
    
    objects = managers.FundManager()
    
    class Meta:
        ordering     = ('code',)
        
    def name(self):
        return self.description
    
    def get_description(self):
        return self.description
    
    def __unicode__(self):
        return u'%s' % self.code
    
    def ccy(self):
        return self.curncy
    
    def root(self):
        if self.parent:
            return self.parent.root()
        else:
            return self
        
    def accounts(self):
        return CustodyAccount.objects.filter(fund=self)
    
    def portfolios(self, **kwargs):
        return Portfolio.objects.filter(fund=self, **kwargs)
    
    def defaultview(self):
        defo = self.portfolioview_set.filter(default = True)
        if defo.count():
            return defo[0]
        else:
            defo = self.portfolioview_set.all()
            if defo.count():
                defo = defo[0]
                defo.default = True
                defo.save()
                return defo
            else:
                p = PortfolioView(fund = self, default = True, code = 'default')
                p.save()
                return p
            
    def can_have_folders(self):
        return self.fund_set.all().count() == 0
    
    def rootfolders(self, view):
        return self.portfolio_set.filter(Q(view = view),
                                         Q(parent__isnull=True))



class Trader(models.Model):
    user            = models.OneToOneField(User, related_name = 'trader')
    fund_holder     = models.ForeignKey(FundHolder, verbose_name = 'team')
    machine         = models.CharField(max_length = 50, blank = True)
    port            = models.IntegerField(default = 9080)
    server_active   = models.BooleanField(default = False)
    default_fund    = models.ForeignKey(Fund, null = True, blank = True)
    default_history = models.PositiveIntegerField(default = 12)
    data            = models.TextField(blank = True)
    
    objects = managers.TraderManager()
    
    class Meta:
        verbose_name = 'people'
        verbose_name_plural = 'people'
        
    
    def fullname(self):
        u = self.user
        if u.first_name and u.last_name:
            return u'%s %s' % (capfirst(u.first_name),capfirst(u.last_name))
        else:
            return u.username
    
    def __unicode__(self):
        return u'%s' % self.user
    
    def is_active(self):
        return self.user.is_active
    is_active.boolean = True
    
    def is_staff(self):
        return self.user.is_staff
    is_staff.boolean = True
    
    def is_superuser(self):
        return self.user.is_superuser
    is_superuser.boolean = True
    
    def has_perm(self, perm):
        return self.user.has_perm(perm)
    
    def servername(self):
        return '%s:%s' % (self.machine, self.port)
    
    def funds(self):
        return self.fund_holder.funds()
    
    def accounts(self):
        funds = self.funds()
        acc   = []
        for f in funds:
            facc = f.accounts()
            for a in facc:
                acc.append(a)
        return acc
    
    def portfolios(self, **kwargs):
        funds = self.funds()
        por = []
        for f in funds:
            fpor = f.portfolios(**kwargs)
            for p in fpor:
                por.append(p)
        return por
    
    def __get_fund_manager(self):
        return self.fund_holder.fund_manager
    fund_manager = property(fget = __get_fund_manager)
    
    

class CustodyAccount(models.Model):
    code   = models.CharField(unique=True, max_length=20)
    name   = models.CharField(max_length=50)
    dummy  = models.BooleanField(default = False)
    fund   = models.ForeignKey(Fund)
    
    objects = managers.CustodyAccountManager()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        ordering = ('id',)
        
        
        
class PortfolioView(TimeStamp):
    '''
    A portfolio view.
    This object defines a portfolio view for a particular Fund
    '''
    fund         = models.ForeignKey(Fund, related_name = 'views')
    name         = models.CharField(max_length=32)
    default      = models.BooleanField(default = False)
    description  = models.TextField(blank = True, null = True)
    user         = models.ForeignKey(User, null = True)
    
    def __unicode__(self):
        return u'%s: %s (%s)' % (self.fund,self.name,self.user)
        #try:
        #    u = self.userportfolioview
        #    return u'%s: %s (%s)' % (self.fund,self.name,u.user)
        #except:
        #    return u'%s: %s' % (self.fund,self.name)
    
    class Meta:
        unique_together = ('fund','name','user')
        
    def save(self):
        default   = self.default
        if default:
            pviews = self.fund.views.all()
            for view in pviews:
                view.default = False
                view.save()
            self.default = True
        super(PortfolioView,self).save()
        
    def set_as_default(self, user):
        '''
        Set the view as default for user 'user'
        '''
        if user and user.is_authenticated():
            des = UserViewDefault.objects.filter(user = user,
                                                 view__fund = self.fund)
            if des:
                des = list(des)
                d = des.pop(0)
                d.view = self
                d.save()
                for d in des:
                    d.delete()
            else:
                d = UserViewDefault(user = user,
                                    view = self)
                d.save()
            return d
        else:
            return None
    
    def is_default(self, user):
        des = self.userviewdefault_set.filter(user = user)
        if des:
            return True
        else:
            return False        
    
    def addFolder(self, parent, code):
        name = code[:32]
        code = code[:22]
        if isinstance(parent,Portfolio) and parent.view == self:
            c = parent.children.filter(code = code)
            if not c:
                c = Portfolio(code   = code,
                              name   = name,
                              parent = parent,
                              view   = parent.view,
                              fund   = parent.fund)
                c.save()
                return c
        elif isinstance(parent,Fund) and parent.can_have_folders():
            c = Portfolio.objects.filter(code = code,
                                         view = self,
                                         fund = parent)
            if not c:
                c = Portfolio(code = code,
                              name = name,
                              view = self,
                              fund = parent)
                c.save()
                return c
        return None
    
    def rootfolders(self):
        return self.portfolio_set.filter()
    


class Portfolio(TimeStamp):
    '''
    Portfolio model.
    If cash_account is set, then this portfolio is treated as a cash account
    '''
    name          = models.CharField(max_length=64)
    description   = models.TextField(blank = True)
    parent        = models.ForeignKey('self', blank=True, null=True, related_name="children")
    view          = models.ForeignKey(PortfolioView, related_name = 'portfolios')
    fund          = models.ForeignKey(Fund)
    position      = models.ManyToManyField('Position', blank = True, null=True)
    cash_account  = models.BooleanField(default = False)
    
    class Meta:
        verbose_name = 'sub portfolio'
        ordering  = ('name',)
        
    def save(self):
        if self.parent:
            self.view = self.parent.view
        super(Portfolio,self).save()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    def subfolders(self):
        return self.children.all()
    
    def setcode(self, code):
        if code:
            self.code = code
    
    def setparent(self, p):
        if isinstance(p,Portfolio):
            self.parent = p
        elif isinstance(p,Fund):
            self.parent = None
        else:
            return
        self.save()
        
    def position_for_date(self, dte, status = None):
        return self.position.positions_for_fund(fund = self.fund, dt = dte, status = status)
    
    def copytoview(self, nview, parent = None):
        folder = Portfolio(code         = self.code,
                           name         = self.name,
                           description  = self.description,
                           view         = nview,
                           fund         = self.fund,
                           cash_account = self.cash_account,
                           parent       = parent)
        folder.save()
        for p in self.position.all():
            folder.position.add(p)
        children = self.children.all()
        for c in children:
            c.copytoview(nview, folder)
        return folder
    
    @staticmethod
    def get_last_modified():
        try:
            p = Portfolio.objects.latest('last_modified')
            return p.last_modified
        except:
            return datetime.date.min


class Position(TimeStamp):
    dataid         = models.ForeignKey('instdata.DataId')
    fund           = models.ForeignKey(Fund)
    dt             = models.DateField(verbose_name = 'date')
    pl             = models.TextField(blank = True)
    status         = models.IntegerField(default=1, choices = managers.position_status_choice)
    size           = models.DecimalField(default = 0,
                                         max_digits = managers.MAX_DIGITS,
                                         decimal_places = managers.ROUNDING)
    value          = models.FloatField(default = 0.0)
    dirty_value    = models.FloatField(default = 0.0)
    cost_unit_base = models.FloatField(default = 0.0)
    book_cost_base = models.FloatField(default = 0.0)
    
    objects = managers.PositionManager()
    
    class Meta:
        get_latest_by   = "dt"
        unique_together = ("dataid", "fund", "dt")
        
    def __unicode__(self):
        return '%s - %s: %s' % (self.dt,self.fund,self.dataid)
    
    @classmethod
    def get_last_modified(cls):
        try:
            p = cls.objects.latest('last_modified')
            return p.last_modified
        except:
            return datetime.date.min
        

class ManualTrade(TimeStamp):
    user            = models.ForeignKey(User)
    dataid          = models.ForeignKey('instdata.DataId')
    fund            = models.ForeignKey(Fund)
    quantity        = models.DecimalField(default = 0,
                                          max_digits = managers.MAX_DIGITS,
                                          decimal_places = managers.ROUNDING)
    open_date       = models.DateField(default = datetime.date.today)
    close_date      = models.DateField(null = True, blank = True)
    price           = models.FloatField(default = 0)
    comment         = models.TextField()
    
    objects = managers.ManualTradeManager()
    
    def __unicode__(self):
        return u'%s (%s)' % (self.dataid,self.open_date)

    @property
    def size(self):
        return self.quantity
            
    
