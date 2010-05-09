#
# Requires django-tagging
#
import datetime

from django.db import models
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from tagging.fields import TagField

from jflow.conf import settings
from jflow.core import frequency, dayCount_choices
from jflow.db import geo
from jflow.db.instdata import managers
from jflow.db.instdata.fields import SlugCode, LazyForeignKey, slugify
from jflow.db.instdata.dynct import ExtraContentModel


field_type = (('numeric','Numeric'),
              ('string','String'),
              ('date','Date'))

Future_Price_Types = (('PRICE','Price'),
                      ('BILL','Bill'),
                      ('RATE','Rate')
                     )

future_type_choice = (
                      ('bond','Bond Future'),
                      ('com','Commodity Future'),
                      ('immirf','IMM Interest Rate Future'),
                      ('eif','Equity Index Future'),
                      ('vif','Volatility Index Future'),
                      )

equity_type = ((1,'Common Stock'),
               (2,'Right'),
               (3,'Unknown')
               )

cash_codes = {1: {'code':'PRI', 'name':'Principal'},
              2: {'code':'INC', 'name':'Income'},
              3: {'code':'BMA', 'name':'Margin'},
              4: {'code':'CAC', 'name':'Call'},
              5: {'code':'SUS', 'name':'Suspense'}
              }

def cash_tuple():
    c = []
    for id, cd in cash_codes.items():
        c.append((id,cd['name']))
    return c

def instrument_query():
    from jflow.db.instdata.utils import instrument_ids
    return {'pk__in': instrument_ids()}


class BaseModel(models.Model):
    code           = SlugCode(max_length = 32, unique = True, upper = True, rtxchar = '_')
    name           = models.CharField(max_length = 64, blank  = True)
    description    = models.TextField(blank=True)
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        abstract = True
  
    
class Vendor(BaseModel):
    '''
    Data Vendor
    '''
    def summary(self):
        return mark_safe(self.description)
    
    def interface(self):
        module   = __import__(settings.VENDOR_MODULE,globals(),locals(),[''])
        return module.get_vendor(self.code)


class DataId(ExtraContentModel):
    '''
    Database ID
    '''
    code           = SlugCode(max_length = 32,
                              db_index = True,
                              unique = True,
                              upper = True)
    #code           = models.CharField(max_length = 32, unique = True)
    name           = models.CharField(max_length = 64, blank  = True)
    description    = models.TextField(blank=True)
    country        = models.CharField(max_length = 2, choices = geo.country_tuples())
    live           = models.BooleanField(default=True)
    default_vendor = models.ForeignKey(Vendor, blank = True, null = True)
    tags           = TagField('labels', blank = True, null = True,
                              help_text = "Insert keywords separated by space")
    isin           = models.CharField(max_length = 32,
                                      blank = True,
                                      default = '',
                                      db_index = True,
                                      verbose_name = 'ISIN') 
    
    # New stuff
    hasdata        = models.BooleanField(default = True, editable = False)
    content_type   = LazyForeignKey(ContentType,
                                    limit_choices_to = instrument_query,
                                    blank=True,
                                    null=True,
                                    verbose_name="instrument")
    firm_code      = models.CharField(blank=True,
                                      max_length=50,
                                      verbose_name = settings.FIRM_CODE_NAME)
    curncy         = models.CharField(max_length=3,
                                      blank = True,
                                      editable = False,
                                      verbose_name='CCY')
    
    objects        = managers.DataIdManager()
        
    def __unicode__(self):
        return self.codename()
    
    def codename(self):
        if self.name:
            return u'%s - %s' % (self.code,self.name)
        else:
            return u'%s' % self.code

    def _denormalize(self, ec = None):
        if ec:
            ec.dataid = self
            ec.code   = self.code
        else:
            ec = self._new_content
            ec.dataid = self
            ec.code   = self.code
            self.curncy = ec.ccy()
    
    def issuer(self, dt = None):
        inst = self.instrument
        if inst:
            return inst.issuer(dt)
        else:
            return None
        
    @property
    def instrument(self):
        return self.extra_content()
    
    @property
    def multiplier(self):
        inst = self.instrument
        if inst:
            return inst.get_multiplier()
        else:
            return 1
        
    def get_country(self):
        return geo.country(self.country)
    get_country.short_description = 'country'
    
    def defaultccy(self):
        return geo.countryccy(self.country)
    
    def __get_dates_range(self):
        try:
            return self.daterange
        except:
            return None
    dates_range = property(fget = __get_dates_range)
    
    def add_issuer(self, issuer):
        inst = self.instrument
        if inst and issuer:
            inst.add_issuer(issuer)

    def keywords(self):
        inst = self.instrument
        if inst:
            return inst.keywords()
        else:
            return None
        
    def get_default_vendor(self):
        return self.default_vendor or settings.DEFAULT_VENDOR_FOR_SITE
    
    def add_vendor(self, vc, ticker):
        if not isinstance(vc,Vendor):
            vc = Vendor.objects.get(code = str(vc).upper())
        try:
            vid = self.vendors.get(vendor = vc)
            if vid.ticker != ticker:
                vid.ticker = ticker
                vid.save()
        except:
            vid = VendorId(ticker = ticker, vendor = vc, dataid = self)
            vid.save()
        return vid


class VendorId(models.Model):
    '''
    Vendor ticker for a given DataId
    For a DataId and a Vendor the entry should be unique.
    This is enforced in the Meta class.
    '''
    ticker = models.CharField(max_length=30)
    vendor = models.ForeignKey(Vendor)
    dataid = models.ForeignKey(DataId, related_name = 'vendors')
    
    def __unicode__(self):
        return '%s' % self.ticker
    
    class Meta:
        unique_together = (("dataid", "vendor"),)
        
    def dbcache(self, field):
        if not isinstance(field,DataField):
            field = DataField.objects.get(code = field)
        return MktDataCache.objects.filter(vendor_id = self, field = field)
        
        
class DataField(models.Model):
    '''
    Field of market data, could be ASK price, BID price, etc...
    '''
    code         = models.CharField(unique=True, max_length=32)
    description  = models.CharField(max_length=60, blank=True)
    format       = models.CharField(max_length=10, choices = field_type)
        
    def __unicode__(self):
        return '%s' % self.code
    
    def get_mkt_data_cls(self):
        format = self.format
        
        if format == 'string':
            return StringMktData
        elif format == 'numeric':
            return MktData
        else:
            raise ValueError("Format %s is not supported" %format)

    

class VendorDataField(models.Model):
    vendor = models.ForeignKey(Vendor)
    field  = models.ForeignKey(DataField)
    code   = models.CharField(max_length = 200, blank = False)
    
    def __unicode__(self):
        return '%s: %s (%s)' % (self.code,self.field,self.vendor)
    
    class Meta:
        unique_together = ('vendor','field')
        

#
#_________________________________________________________ INFO MODELS

class Exchange(models.Model):
    code = models.CharField(unique=True, max_length=12)
    name = models.CharField(max_length=50, blank=True)
        
    def __unicode__(self):
        if self.name:
            if self.name == self.code:
                return self.code
            else:
                return u'%s - %s' % (self.code,self.name)
        else:
            return self.code


class FutureContract(models.Model):
    code           = models.CharField(unique=True, max_length=12)
    curncy         = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    country        = models.CharField(max_length = 2, choices = geo.country_tuples())
    exchange       = models.ForeignKey(Exchange,null=True,blank=True)
    description    = models.CharField(max_length=60,blank=True)
    price_type     = models.CharField(max_length=10,choices=Future_Price_Types,blank=True)
    index          = models.ForeignKey(DataId,null=True,blank=True)
    expiry_months  = models.CharField(max_length=24,blank=True)
    trading_unit   = models.CharField(max_length=32,blank=True)
    tick_size      = models.FloatField()
    tick_value     = models.FloatField()
    ticket_cost    = models.FloatField(default=0.0)
    term_structure = models.IntegerField(default = 0)
    type           = models.CharField(max_length=12, choices = future_type_choice)
        
    def __unicode__(self):
        return u'%s - %s' % (self.code,self.description)
        
    def tonotional(self, size):
        return self.tick_value*size/self.tick_size
        
    def blbcom(self):
        ac = str(self.asset_class.code)
        if ac == 'EQ':
            return 'Index'
        else:
            return 'Comdty'

class IndustryCode(models.Model):
    id           = models.IntegerField(primary_key=True)
    code         = models.CharField(unique=True, max_length=64)
    description  = models.TextField(blank=True)
    parent       = models.ForeignKey('self', null = True, blank = True)
    
    objects = managers.IndustryCodeManager()
    
    def __unicode__(self):
        return u'%s - %s' % (self.id, self.code)
    
    def keywords(self):
        key = slugify(self.code.replace('/',' '),'_')
        keys = key.split('_')
        kk = []
        if self.parent:
            keys.extend(self.parent.keywords())
        for key in keys:
            key = key.lower()
            if key not in kk:
                kk.append(key)
        return kk
                
    
class CollateralType(models.Model):
    name = models.CharField(max_length=60,unique=True)
    order = models.PositiveIntegerField(default = 1)
    
    class Meta:
        ordering  = ('order',)
        
    def __unicode__(self):
        return self.name
    
  
class BondMaturityType(models.Model):
    code = models.CharField(unique=True, max_length=32)
    description = models.CharField(blank=True,max_length = 255)
        
    def __unicode__(self):
        return u'%s' % self.code

class BondClass(models.Model):
    code             = models.CharField(unique=True,max_length=12)
    curncy           = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    country          = models.CharField(max_length = 2, choices = geo.country_tuples())
    description      = models.CharField(max_length=60,blank=True)
    price_type       = models.CharField(max_length=10,choices=Future_Price_Types,blank=True)
    index            = models.ForeignKey('DataId',null=True,blank=True)
    sovereign        = models.BooleanField(default=False)
    convertible      = models.BooleanField(default=False)
    bondcode         = models.CharField(null=True,max_length=12)
    
    class Meta:
        verbose_name_plural = 'Bond Classes'
        ordering = ('code',)
        
    def fulldescription(self):
        return '%s bond. %s' % (self.description,
                                self.coupon_type)
        
    def __unicode__(self):
        return self.code
        
    def settlement(self):
        return 'T + %s' % self.settlement_delay
    
    def issuer(self, dt = None):
        dt = dt or datetime.date.today()
        iss = self.issuers.filter(dt__lte = dt)
        if iss:
            return iss.latest().issuer
        else:
            iss = self.issuers.all()
            if iss:
                #TODO: this should not be latest, but the earliest!
                return iss.latest().issuer
            else:
                return None
        
    def add_issuer(self, issuer, dt = None):
        if not issuer:
            return
        dt = dt or datetime.date.today()
        old_issuer = self.issuer(dt)
        if old_issuer == issuer:
            return
        bi , created = BondIssuer.objects.get_or_create(dt = dt, issuer = issuer, bond_class = self)
        bi.save()
        
        return bi

class FundType(BaseModel):
    openended   = models.BooleanField(default = False)

class FundStrategy(BaseModel):
    pass
      
class FundManager(BaseModel):
    '''
    Fund manager detail
    '''
    address          = models.CharField(max_length=200, blank = True)
    website          = models.CharField(max_length=100, null = True, blank = True)
    

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
#
#__________________________________________________________ INSTRUMENTS

class InstrumentInterface(models.Model):
    InstrumentFactory = None
    
    code       = models.CharField(unique=True, max_length=32, editable = False)
    dataid     = models.OneToOneField(DataId, editable = False)
    
    class Meta:
        abstract = True
        
    @property
    def country(self):
        return self.dataid.country
    
    def ccy(self):
        return ''
    
    def get_multiplier(self):
        return 1
    
    def keywords(self):
        return None
    
    def isin(self):
        return self.dataid.isin
    
    def issuer(self, dt = None):
        return None
    
    def add_issuer(self, issuer):
        pass
    
    def metadata(self):
        return []
                 
    

class Security(InstrumentInterface):
    CUSIP            = models.CharField(max_length=30,blank=True)
    SEDOL            = models.CharField(max_length=30,blank=True)
    exchange         = models.ForeignKey('exchange',null=True,blank=True)
    
    class Meta:
        abstract = True
        
    
    def metadata(self):
        data = []
        if self.exchange:
            data.append({'name':'exchange','value':self.exchange})
        return data
    

class EquityBase(Security):
    curncy           = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
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


class Future(InstrumentInterface):
    contract            = models.ForeignKey(FutureContract)
    first_trade         = models.DateField()
    last_trade          = models.DateField()
    first_notice        = models.DateField()
    first_delivery      = models.DateField()
    last_delivery       = models.DateField()
    
    def ccy(self):
        return self.contract.curncy

    ###Added here ####
    objects = managers.FutureManager()
    ##################
class Equity(EquityBase):
    industry_code     = models.ForeignKey(IndustryCode,null=True,blank=True)
    security_type     = models.SmallIntegerField(choices = equity_type, default = 1, null = True, blank = True)
    related           = models.ForeignKey('self', null = True, blank = True)
    
    objects = managers.EquityManager()
    
    class Meta:
        verbose_name_plural = 'equities'
    
    def need_value_date(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)
    
    def check(self):
        if super(Equity,self).check():
            return self._check_id()
        return False
    
    def keywords(self):
        if self.industry_code:
            keys = self.industry_code.keywords()
        else:
            keys = []
        if 'equity' not in keys:
            keys.append('equity')
        return keys


class Etf(EquityBase):
    
    objects = managers.EtfManager()
        
    class Meta:
        verbose_name = 'ETF'
        verbose_name_plural = 'ETFs'
        
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)


class Fund(EquityBase):
    manager            = models.ForeignKey(FundManager, null=True, blank = True)
    type               = models.ForeignKey(FundType, null=True, blank = True)
    strategy           = models.ForeignKey(FundStrategy, null=True, blank = True)
    domicile           = models.CharField(max_length = 2, choices = geo.country_tuples(), help_text="Fund domicile")
    status             = models.BooleanField(default=True) # Fund open or closed
    established        = models.DateField(null=True, blank = True)   
    
    objects = managers.FundManager()
    
    def make_position(self, **kwargs):
        return FACTORY.equity(inst = self, **kwargs)
    
    def infodict(self):
        r = super(Fund,self).infodict()
        if self.type:
            r['Type'] = self.type.name
            r['Open ended'] = self.type.openended
        return r


class Bond(Security):
    bond_class          = models.ForeignKey(BondClass,related_name='bondspec')
    coupon              = models.DecimalField(max_digits=12, decimal_places = 6, null = True, blank = True)
    announce_date       = models.DateField(null = True, blank = True)
    first_settle_date   = models.DateField(null = True, blank = True)
    first_coupon_date   = models.DateField(null = True, blank = True)
    accrual_date        = models.DateField(null = True, blank = True)
    maturity_date       = models.DateField(null = True, blank = True)
    collateral_type     = models.ForeignKey(CollateralType)
    multiplier          = models.FloatField(default = 0.01)
    month_frequency     = models.IntegerField(default=12)
    day_count           = models.CharField(choices = dayCount_choices, max_length=20)
    settlement_delay    = models.SmallIntegerField(default = 3)
    callable            = models.BooleanField(default=False)
    putable             = models.BooleanField(default=False)
    
    objects = managers.BondManager()
    
    def get_multiplier(self):
        return self.multiplier
    
    def ccy(self):
        return self.bond_class.curncy

    def issuer(self, dt = None):
        return self.bond_class.issuer(dt)
    
    def add_issuer(self, issuer):
        self.bond_class.add_issuer(issuer)
        
    def keywords(self):
        issuer = self.issuer()
        if issuer:
            keys = issuer.keywords()
            try:
                keys.remove('equity')
            except:
                pass
        else:
            keys = []
        if 'bond' not in keys:
            keys.append('bond')
        return keys


class BondIssuer(models.Model):
    bond_class = models.ForeignKey(BondClass, related_name = 'issuers')
    issuer     = models.ForeignKey(DataId, related_name = 'bond_issuers')
    dt         = models.DateField()
    
    def __unicode__(self):
        return u'%s' % self.issuer
    
    class Meta:
        unique_together = (("bond_class", "issuer", "dt"),)
        get_latest_by = 'dt'
        
    def ccy(self):
        return self.bond_class.curncy
        
    def __get_data_id(self):
        return self.issuer.data_id
    data_id = property(fget = __get_data_id)
    

class Cash(InstrumentInterface):
    curncy      = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    cash_type   = models.IntegerField(choices = cash_tuple(), default = 1)
    extended    = models.TextField(blank = True)
    
    objects = managers.CashManager()
    
    def codeinfo(self):
        return cash_codes.get(self.type,None)
    
    def has_firm_code(self):
        return False
    
    def name(self):
        return self.description()
    
    def description(self):
        ci = self.codeinfo()
        va = 'Cash %s' % self.curncy
        if ci:
            return '%s %s' % (va,ci['name'])
        else:
            return va
    
    class Meta:
        verbose_name = 'cash'
        verbose_name_plural = 'cash'
        
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
        
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, **kwargs)


class FwdCash(InstrumentInterface):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    value_date = models.DateField()
    
    objects = managers.FwdCashManager()
    
    class Meta:
        verbose_name = 'forward cash'
        verbose_name_plural = 'forward cash'
        
    def description(self):
        return 'Forward %s cash %s' % (self.curncy, self.value_date)
    
    def name(self):
        return self.description()
    
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, value_date = self.value_date, **kwargs)
    

class Depo(InstrumentInterface):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    value_date = models.DateField()
    
    objects = managers.FwdCashManager()
    
    def description(self):
        return '%s Deposit: expiry %s' % (self.curncy, self.value_date)
    
    def name(self):
        return self.description()
    
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, value_date = self.value_date, **kwargs)

##### Added here to manage generic securities
class GenericOTC(InstrumentInterface):
    
    objects = managers.GenericOTCManager()

######       

class InstDecomp(models.Model):
    code         = models.CharField(max_length = 255, blank = True)
    dataid       = models.ForeignKey(DataId)
    dt           = models.DateField(verbose_name='date')
    composition  = models.TextField()
    description  = models.TextField(blank = True)
    
    objects = managers.DecompManager()
    
    def __unicode__(self):
        return self.composition
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.dataid.code
        super(InstDecomp,self).save(*args, **kwargs)
    
    @property
    def instrument(self):
        return self.dataid.instrument    
    
    class Meta:
        verbose_name = 'Instrument Decomposition'
        verbose_name_plural = 'Instrument Decomposition'
        unique_together = ('code', 'dataid', 'dt')
        get_latest_by   = 'dt'



#_____________________________________________________ MARKET DATA
class MktDataBase(models.Model):
    vendor_id    = models.ForeignKey(VendorId)
    field        = models.ForeignKey(DataField)
    dt           = models.DateField(verbose_name='date')
    
    class Meta:
        abstract = True
        

class MktData(MktDataBase):
    mkt_value  = models.FloatField(default=0, blank=True, verbose_name='market value')
    
    class Meta:
        verbose_name_plural = 'Market Data'
        get_latest_by   = 'dt'
        

class StringMktData(MktDataBase):
    mkt_value    = models.TextField(blank=True, verbose_name='market value')
    
    class Meta:
        verbose_name_plural = 'String Market Data'
        get_latest_by   = 'dt'

class MktDataCache(MktDataBase):
    mkt_value    = models.FloatField(default=0, blank=True, verbose_name='market value')
    
    objects = managers.MktDataCacheManager()
    
    class Meta:
        ordering = ('dt',)
        get_latest_by   = 'dt'
        

class EconometricAnalysis(models.Model):
    user    = models.ForeignKey(User)
    command = models.TextField()
    title   = models.CharField(max_length = 64, blank = True)
    description = models.TextField(blank = True)
    tags        = TagField('labels', blank = True, null = True,
                           help_text = "Insert keywords separated by space")
    class Meta:
        unique_together = ('user','command')

    def __unicode__(self):
        return self.title or self.command
