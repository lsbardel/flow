from django.db import models

from jflow.db.trade.managers import FundManager
from jflow.db import geo


class FundHolder(models.Model):
    code         = models.CharField(unique=True, max_length=10)
    description  = models.CharField(max_length=255, blank = True)
    fund_manager = models.BooleanField(default = False)
    
    class Meta:
        verbose_name = 'team'
        ordering     = ('code',)
    
    def __unicode__(self):
        return u'%s' % self.code


class Fund(models.Model):
    code            = models.CharField(unique=True, max_length=10)
    firm_code       = models.CharField(unique=True, max_length=50)
    description     = models.CharField(max_length=255, blank = True)
    fund_holder     = models.ForeignKey(FundHolder, verbose_name = 'team', related_name = 'funds')
    curncy          = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    parent          = models.ForeignKey('self', null = True, blank = True)
    dataid          = models.ForeignKey('instdata.DataId',
                                        blank = True,
                                        null = True,
                                        related_name = 'dataid')
    
    objects = FundManager()
    
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

