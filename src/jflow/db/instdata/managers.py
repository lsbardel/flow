from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms.models import modelform_factory

from tagging.managers import ModelTaggedItemManager

from jflow.db.instdata.converters import convert
from jflow.db.instdata.fields import slugify
from jflow.db.instdata.settings import DEFAULT_VENDOR_FOR_SITE


class MktDataCacheManager(models.Manager):
    
    def emptycache(self, dataid = None):
        if isinstance(dataid, models.Model):
            qs = self.filter(vendor_id__dataid = dataid)
        else:
            qs = self.all()
        qs.delete()


class DataIdManager(ModelTaggedItemManager):
    
    def ct_from_type(self, type):
        '''
        Return content type object from type name
        '''
        app_label = self.model._meta.app_label
        return ContentType.objects.get(name = type, app_label = app_label)
    
    def ctmodel(self, type):
        if type:
            try:
                ct = self.ct_from_type(type)
                return ct, ct.model_class()
            except:
                raise ValueError('Data type %s not available' % type)
        else:
            return None,None
    
    def for_type(self, type):
        try:
            ct = self.ct_from_type(type)
        except:
            return self.none()
        return self.filter(content_type = ct)
    
    def get_or_create(self,
                      commit = True,
                      type = None,
                      country = None,
                      default_vendor = None,
                      **kwargs):
        '''
        Override get_or_create.
        
        kwargs must contain:
            code
            country
            default_vendor
        
        Optional
            type
            tags         
        '''
        code = kwargs.pop('code',None)
        if not code:
            raise ValueError('cannot add data id, code not specified')
        code = slugify(code.upper())
        try:
            id = self.get(code = code)
            created = False
            if default_vendor:
                default_vendor  = convert('vendor', default_vendor)
        except:
            id = None
            default_vendor  = convert('vendor', default_vendor or DEFAULT_VENDOR_FOR_SITE)
            created = True
        
        if default_vendor:
            default_vendor = default_vendor.id
        ct, model = self.ctmodel(type)
        country = convert('country', country)
        
        id = model.objects.create(id,
                                  commit = commit,
                                  code = code,
                                  country = country,
                                  default_vendor = default_vendor,
                                  **kwargs)
        return id,created
        
        
class InstrumentManager(models.Manager):
    
    def safeint(self, val, default):
        try:
            return int(val)
        except:
            return default
    
    def safefloat(self, val, default):
        try:
            return float(val)
        except:
            return default
    
    def get_data(self, id,
                 code = '',
                 default_vendor = None, 
                 country = None,
                 firm_code = '',
                 name = '',
                 description = '',
                 isin = '',
                 tags = '',
                 **kwargs):
        live = True
        if id:
            live = id.live
            isin = isin or id.isin
        data = {'code': code,
                'default_vendor': default_vendor,
                'country': country,
                'content_type': ContentType.objects.get_for_model(self.model).id,
                'live': live,
                'isin': isin}
        if firm_code:
            data['firm_code'] = firm_code
        if name:
            data['name'] = name
        if description:
            data['description'] = description
        if tags:
            data['tags'] = tags
        return data
        
    def create(self, id, **kwargs):
        from jflow.db.instdata.forms import DataIdForm
        data = self.get_data(id, **kwargs)
        f = DataIdForm(data,instance=id)
        if f.is_valid():
            return f.save()
        else:
            return None
         

class SecurityManager(InstrumentManager):
    
    def get_data(self, id, CUSIP = '',
                 SEDOL = '', exchange = '', **kwargs):
        data = super(SecurityManager,self).get_data(id, **kwargs)
        exchange = convert('exchange', exchange)
        if exchange:
            exchange = exchange.id
        data.update({'CUSIP': CUSIP,
                     'SEDOL': SEDOL,
                     'exchange': exchange})
        return data

class EtfManager(SecurityManager):
    
    def get_data(self, id, curncy = '', multiplier = 1,
                 settlement_delay = 2, **kwargs):
        data = super(EtfManager,self).get_data(id, **kwargs)
        data.update({'curncy': convert('curncy',curncy),
                     'multiplier': self.safefloat(multiplier,1),
                     'settlement_delay': self.safeint(settlement_delay,2)})
        return data
    
class EquityManager(SecurityManager):
    
    def get_data(self, id, curncy = '', multiplier = 1,
                 settlement_delay = 2,  security_type = 1,
                 sector = None, sectorid = None,
                 group = None, groupid = None,
                 industry_code = None,
                 commit = True, **kwargs):
        if not industry_code:
            #TODO remove thid import and obtain moel from self.model 
            from jflow.db.instdata.models import IndustryCode as secmodel
            #secmodel = self.model._name_map.get('industry_code')[0]
            industry_code = secmodel.objects.create(sector, sectorid, group, groupid)
            if industry_code:
                industry_code = industry_code.id
        data = super(EquityManager,self).get_data(id, **kwargs)
        data.update({'industry_code': industry_code,
                     'curncy': convert('curncy',curncy),
                     'multiplier': self.safefloat(multiplier,1),
                     'settlement_delay': self.safeint(settlement_delay,2),
                     'security_type': convert('security_type',security_type)})
        return data
    
class FundManager(SecurityManager):
    
    def get_data(self, id, curncy = '', multiplier = 1,
                 settlement_delay = 2,  security_type = 1,
                 commit = True,
                 **kwargs):
        data = super(FundManager,self).get_data(id, **kwargs)
        data.update({'curncy': convert('curncy',curncy),
                     'multiplier': self.safefloat(multiplier,1),
                     'settlement_delay': self.safeint(settlement_delay,2)})
        return data
    
class BondManager(SecurityManager):
    
    def get_data(self, id,
                 curncy            = '',
                 bondclass__code   = None,
                 collateral_type   = None,
                 announce_date     = None,
                 first_settle_date = None,
                 first_coupon_date = None,
                 accrual_date      = None,
                 maturity_date     = None,
                 multiplier        = None,
                 settlement_delay  = None,
                 coupon            = None,
                 month_frequency   = 0,
                 day_count         = None,
                 callable          = False,
                 putable           = False,
                 commit            = True, 
                 **kwargs):
        data = super(BondManager,self).get_data(id, **kwargs)
        ccy = convert('curncy',curncy)
                     
        bck = {}
        for k,v in kwargs.items():
            ks = k.split('__')
            if len(ks) == 2 and ks[0] == 'bondclass':
                    bck[ks[1]] = v
        
        bc = bck.pop('bondcode',None)
        co = data.get('country',None)
        bc = convert('bondclass',bc,curncy=ccy,country=co,**bck)
        
        data.update({'curncy':              ccy,
                     'bond_class':          bc.id,
                     'announce_date':       convert('bonddate',announce_date),
                     'first_settle_date':   convert('bonddate',first_settle_date),
                     'first_coupon_date':   convert('bonddate',first_coupon_date),
                     'accrual_date':        convert('bonddate',accrual_date),
                     'maturity_date':       convert('bonddate',maturity_date),
                     'collateral_type':     convert('collateral',collateral_type).id,
                     'multiplier':          self.safefloat(multiplier,0.01),
                     'settlement_delay':    self.safeint(settlement_delay,3),
                     'coupon':              self.safefloat(coupon,0),
                     'month_frequency':     self.safeint(month_frequency, 0),
                     'day_count':           convert('daycount',day_count),
                     'callable':            callable,            
                     'putable':             putable,
                     })
        return data
    
        

class DecompManager(models.Manager):
    
    def for_object(self, id, code = None, dt = None):
        code = code or id.code
        v = self.filter(dataid = id, code = code)
        if not dt:
            v = v.latest
        return v.composition
        

class IndustryCodeManager(models.Manager):
    
    def create(self, sector, sectorid, group, groupid):
        if sector and sectorid and group and groupid:
            try:
                sid  = int(sectorid)
                gid  = int(groupid)
            except:
                return None
            sector, created = self.get_or_create(id = sid, code = sector)
            group, created = self.get_or_create(id = gid, code = group)
            group.parent = sector
            group.save()
            return group
        else:
            return None

