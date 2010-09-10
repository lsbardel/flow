from base import *
from jflow.core import frequency


class CodeDescriptionModel(models.Model):
    code = models.CharField(unique = True, max_length=32)
    name = models.CharField(max_length=62, blank = True)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        n = self.name
        if n:
            return u'%s - %s' % (self.code,n)
        else:
            return u'%s' % self.code
        
    class Meta:
        abstract = True


class FundType(CodeDescriptionModel):
    openended   = models.BooleanField(default = False)
    class Meta:
        app_label    = current_app_label


class FundStrategy(CodeDescriptionModel):
    class Meta:
        app_label    = current_app_label
      
      
class FundManager(CodeDescriptionModel):
    '''
    Fund manager detail
    '''
    address          = models.CharField(max_length=200, blank = True)
    website          = models.CharField(max_length=100, null = True, blank = True)
    
    class Meta:
        app_label    = current_app_label
    

pct_text='as a percentage, i.e 10 for 10%'
class FundLiquidity(models.Model):
    management_fee     = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank = True, help_text=pct_text)
    performance_fee    = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank = True, help_text=pct_text)
    admin_fee          = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank = True, help_text=pct_text)
    redemption_fee     = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank = True, help_text=pct_text)
    other_fee          = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank = True, help_text=pct_text)    
    highwatermark      = models.BooleanField(default=False)
    hurdle             = models.BooleanField(default=False)
    dealing_frequency  = models.CharField(max_length = 6, choices = frequency.frequencytuple())
    minimum_investment = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank = True)
    lockup_days        = models.PositiveIntegerField(null = True, blank = True)
    redemption_notice_days = models.PositiveIntegerField(null = True, blank = True) # notice no. days 
    redemption_payout_days = models.PositiveIntegerField(null = True, blank = True) # no. days until payout
    liquidity              = models.OneToOneField('Fund')
    
    class Meta:
        app_label    = current_app_label
        
        
        
