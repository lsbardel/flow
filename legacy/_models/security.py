from django.utils.dateformat import format 

from fund import *
from instrument import FincialInstrumentBase
from jflow.db import geo
import factory as FACTORY
from master import BondClass, CollateralType

__all__ = ['SecurityBase',
           'Future',
           'Security',
           'Equity',
           'Etf',
           'Fund',
           'Bond',
           'BondIssuer',
           'Warrant',
           'WarrantExerciseDate']

class SecurityBase(FincialInstrumentBase):
    
    class Meta:
        abstract = True
            
    def get_data_id(self):
        return self.code.data_id
        
    def country(self):
        return self.code.data_id.country
    
    def description(self):
        return self.code.data_id.description
    
    def name(self):
        return self.code.data_id.name

class Future(SecurityBase):
    contract            = models.ForeignKey('FutureContract')
    first_trade         = models.DateField()
    last_trade          = models.DateField()
    first_notice        = models.DateField()
    first_delivery      = models.DateField()
    last_delivery       = models.DateField()

    class Meta:
        app_label = current_app_label
        ordering  = ('contract','first_notice')
        
    def __get_exchange(self):
        return self.contract.exchange
    exchange = property(fget = __get_exchange)
    
    def get_underlying(self):
        return self.contract.index
            
    def ccy(self):
        return self.contract.curncy
    
    def Contract(self):
        return self.contract
    
    #def instype(self):
    #    return self.contract.type
        
    def end_date(self):
        return self.first_notice
    
    def live(self):
        to = datetime.date.today()
        return to <= self.last_trade
    
    def isotc(self):
        return False
    
    def tonotional(self, size):
        return self.contract.tonotional(size)
    
    def GetDateRange(self):
        from prospero.contrib.data.models import DateRange
        start = self.first_trade
        end   = self.last_trade
        return DateRange(start = start, end = end)
    
    def check(self):
        if super(Future,self).check():
            return self._check_id()
        return False            
    
    def make_position(self, **kwargs):
        return FACTORY.future(inst = self, **kwargs)
    
    def infodict(self):
        df = settings.DATE_FORMAT
        r  = super(Future,self).infodict()
        r.update({'first_trade': format(self.first_trade,df),
                  'last_trade': format(self.last_trade,df),
                  'first_notice': format(self.first_notice,df),
                  'first_delivery': format(self.first_delivery,df),
                  'last_delivery': format(self.last_delivery,df)})
        return r



class Security(SecurityBase):
    curncy           = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    ISIN             = models.CharField(max_length=30,blank=True)
    CUSIP            = models.CharField(max_length=30,blank=True)
    SEDOL            = models.CharField(max_length=30,blank=True)
    exchange         = models.ForeignKey('exchange',null=True,blank=True)
    multiplier       = models.FloatField(default = 1)
    settlement_delay = models.SmallIntegerField(default = 2)

    class Meta:
        abstract = True
        
    def ccy(self):
        return self.curncy
    
    def sett_delay(self):
        return self.settlement_delay
    
    def isotc(self):
        return False
    
    def get_multiplier(self):
        return self.multiplier
    
    def infodict(self):
        df = settings.DATE_FORMAT
        r = super(Security,self).infodict()
        if self.ISIN:
            r['ISIN'] = self.ISIN
        if self.exchange:
            r['Exchange'] = self.exchange.code
        return r
    
    
class Equity(Security):
    industry_code     = models.ForeignKey('IndustryCode',null=True,blank=True)
    security_type     = models.SmallIntegerField(choices = equity_type, default = 1, null = True, blank = True)
    related           = models.ForeignKey('self', null = True, blank = True)
    
    class Meta:
        app_label    = current_app_label
        verbose_name_plural = 'equities'
        
    def ccy(self):
        return self.curncy
    
    def need_value_date(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)
    
    def check(self):
        if super(Equity,self).check():
            return self._check_id()
        return False

class Etf(Security):
        
    class Meta:
        app_label    = current_app_label
        verbose_name = 'ETF'
        verbose_name_plural = 'ETFs'
        
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)
        
class Fund(Security):
    manager            = models.ForeignKey(FundManager, null=True, blank = True)
    type               = models.ForeignKey(FundType, null=True, blank = True)
    strategy           = models.ForeignKey(FundStrategy, null=True, blank = True)
    domicile           = models.CharField(max_length = 2, choices = geo.country_tuples(), help_text="Fund domicile")
    status             = models.BooleanField(default=True) # Fund open or closed
    established        = models.DateField(null=True, blank = True)   
    
    class Meta:
        app_label    = current_app_label
        
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)
    
    def infodict(self):
        r = super(Fund,self).infodict()
        if self.type:
            r['Type'] = self.type.name
            r['Open ended'] = self.type.openended
        return r


class Bond(SecurityBase):
    bond_class          = models.ForeignKey('BondClass',related_name='bondspec')
    ISIN                = models.CharField(max_length=30,blank=True, null=True)
    CUSIP               = models.CharField(max_length=30,blank=True, null=True)
    coupon              = models.DecimalField(max_digits=12, decimal_places = 6, null = True, blank = True)
    announce_date       = models.DateField(null = True, blank = True)
    first_settle_date   = models.DateField(null = True, blank = True)
    first_coupon_date   = models.DateField(null = True, blank = True)
    accrual_date        = models.DateField(null = True, blank = True)
    maturity_date       = models.DateField(null = True, blank = True)
    collateral_type     = models.ForeignKey(CollateralType)
    
    #month_frequency  = models.IntegerField(default=12)
    #day_count        = models.CharField(choices = dayCount_choices, max_length=20)
    #settlement_delay = models.SmallIntegerField(default = 3)
    #callable         = models.BooleanField(default=False)
    #putable          = models.BooleanField(default=False)
    
    class Meta:
        app_label  = current_app_label
        ordering   = ('bond_class','maturity_date',)
    
    def get_multiplier(self):
        return 0.01
    
    def sett_delay(self):
        return self.bond_class.settlement_delay
    
    def ccy(self):
        return self.bond_class.curncy
    
    def Contract(self):
        return self.bond_class
        
    def end_date(self):
        return self.maturity_date
    
    def live(self):
        to = datetime.date.today()
        return to <= self.maturity_date
    
    def isotc(self):
        return False
    
    def check(self):
        if super(Bond,self).check():
            return self._check_id()
        return False
    
    def need_value_date(self):
        return True
    
    def GetDateRange(self):
        from prospero.contrib.data.models import DateRange
        start = self.announce_date
        end   = self.maturity_date
        return DateRange(start = start, end = end)
    
    def make_position(self, **kwargs):
        return FACTORY.bond(inst = self, **kwargs)
    
    def infodict(self):
        df = settings.DATE_FORMAT
        r = super(Bond,self).infodict()
        if self.ISIN:
            r['ISIN'] = self.ISIN
        if self.coupon:
            r['Coupon'] = float(str(self.coupon))
        if self.maturity_date:
            r['Maturity'] = format(self.maturity_date,df)
        else:
            r['Maturity'] = 'Perpetual'
        if self.announce_date:
            r['Announce date']  = format(self.announce_date,df)
        if self.announce_date:
            r['Announce']  = format(self.announce_date,df)
        if self.first_settle_date:
            r['First settle']  = format(self.first_settle_date,df)
        if self.first_coupon_date:
            r['First coupon']  = format(self.first_coupon_date,df)
        if self.accrual_date:
            r['Accrual']  = format(self.accrual_date,df)
        if self.collateral_type:
            r['Collateral'] = str(self.collateral_type)
        return r
    
    
class BondIssuer(models.Model):
    bond_class = models.ForeignKey(BondClass)
    issuer     = models.ForeignKey(Equity, related_name = 'issuers')
    dt         = models.DateField()
    
    def __unicode__(self):
        return u'%s' % self.issuer
    
    class Meta:
        app_label  = current_app_label
        unique_together = (("bond_class", "issuer", "dt"),)
        ordering = ('bond_class',)
        get_latest_by = 'dt'
        
    def ccy(self):
        return self.bond_class.curncy
        
    def __get_data_id(self):
        return self.issuer.data_id
    data_id = property(fget = __get_data_id)



class Warrant(Security):
    underlying    = models.ForeignKey('dataid')
    strike        = models.FloatField(null = True, blank = True)
    issue_date    = models.DateField(null = True, blank = True)
    expiry        = models.DateField(null = True, blank = True)
    exercise_type = models.PositiveSmallIntegerField(choices = Exercise_Types)
    settle_type   = models.PositiveSmallIntegerField(default = 1, choices = Settle_Types)
    
    def make_position(self, **kwargs):
        return FACTORY.warrant(inst = self, **kwargs)
    
    class Meta:
        app_label  = current_app_label
        
    def get_underlying(self):
        return self.underlying
        
class WarrantExerciseDate(models.Model):
    warrant = models.ForeignKey(Warrant, related_name = 'exercise')
    dt      = models.DateField()
    
    class Meta:
        app_label  = current_app_label

