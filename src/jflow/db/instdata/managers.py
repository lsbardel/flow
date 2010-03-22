from django.contrib.contenttypes.models import ContentType
from django.db import models

from tagging.managers import ModelTaggedItemManager

from jflow.db.instdata.converters import convert
from jflow.db.instdata.settings import DEFAULT_VENDOR_FOR_SITE


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
    
    def get_or_create(self, commit = True, **kwargs):
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
        try:
            id = self.get(code = code)
            created = False
        except:
            id = self.model(code = code)
            if commit:
                id.save()
            created = True
        
        if created:
            return self.create(id, commit = commit, **kwargs), True
        else:
            return self.modify(id, commit = commit, **kwargs), False
        
    def create(self, id,
               commit = True,
               type = None,
               country = None,
               default_vendor = None, **kwargs):
        '''
        Create a new instrument
        '''
        ct, model = self.ctmodel(type)
        id.default_vendor  = convert('vendor', default_vendor or DEFAULT_VENDOR_FOR_SITE)
        id.country = convert('country', country)
        if ct:
            id._new_content = model.objects.create(id, commit = commit, **kwargs)
            id.content_type = ct
        if commit:
            id.save()
        return id
        
    def modify(self, id,
               commit = True,
               type = None,
               country = None,
               default_vendor = None, **kwargs):
        ct, model = self.ctmodel(type)
        if default_vendor:
            id.default_vendor  = convert('vendor', default_vendor)
        if country:
            id.country = convert('country', country)
        if ct:
            inst = id.instrument
            if inst:
                if not isinstance(inst,model):
                    inst.delete()
                    inst = model.objects.create(id, commit = commit, **kwargs)
            id._new_content = inst
        if commit:
            id.save()
        return id
        
        
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

class SecurityManager(InstrumentManager):
    
    def create(self, id, ISIN = '', CUSIP = '', SEDOL = '', exchange = '', **kwargs):
        exchange = convert('exchange', exchange)
        return self.model(dataid = id, code = id.code,
                          ISIN = ISIN, CUSIP = CUSIP,
                          SEDOL = SEDOL, exchange = exchange)

class EtfManager(SecurityManager):
    
    def create(self, id, curncy = '', multiplier = 1,
               settlement_delay = 2, **kwargs):
        obj = super(EtfManager,self).create(id, **kwargs)
        obj.curncy = convert('curncy',curncy)
        obj.multiplier = self.safefloat(multiplier,1)
        obj.settlement_delay = self.safeint(settlement_delay,2)
        obj.save()
        return obj
    
class EquityManager(SecurityManager):
    
    def create(self, id, curncy = '', multiplier = 1,
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
        obj = super(EquityManager,self).create(id, **kwargs)
        obj.industry_code = industry_code
        obj.curncy = convert('curncy',curncy)
        obj.multiplier = self.safefloat(multiplier,1)
        obj.settlement_delay = self.safeint(settlement_delay,2)
        obj.security_type = convert('security_type',security_type)
        if commit:
            obj.save()
        return obj
    
                

class FundManager(SecurityManager):
    
    def create(self, id, curncy = '', multiplier = 1,
               settlement_delay = 2,  security_type = 1,
               commit = True,
               **kwargs):
        obj = super(FundManager,self).create(id, **kwargs)
        obj.curncy = convert('curncy',curncy)
        obj.multiplier = self.safefloat(multiplier,1)
        obj.settlement_delay = self.safeint(settlement_delay,2)
        obj.security_type = convert('security_type',security_type)
        if commit:
            obj.save()
        return obj
    
class BondManager(SecurityManager):
    
    def create(self, id,
               curncy            = '',
               country           = '',
               bondclass__code   = None,
               collateral_type   = None,
               announce_date     = None,
               first_settle_date = None,
               first_coupon_date = None,
               accrual_date      = None,
               maturity_date     = None,
               multiplier        = None,
               settlement_delay  = None,
               commit            = True,
               **kwargs):
        obj = super(BondManager,self).create(id, **kwargs)
        obj.announce_date       = convert('bonddate',announce_date)
        obj.first_settle_date   = convert('bonddate',first_settle_date)
        obj.first_coupon_date   = convert('bonddate',first_coupon_date)
        obj.accrual_date        = convert('bonddate',accrual_date)
        obj.maturity_date       = convert('bonddate',maturity_date)
        obj.collateral_type     = convert('collateral',collateral_type)
        
        ccy = convert('curncy',curncy)
        country = id.country
        bck = {}
        isu = {}
        for k,v in kwargs.items():
            ks = k.split('__')
            if len(ks) == 2 and ks[0] == 'bondclass':
                    bck[ks[1]] = v
        
        bc = bck.pop('bondcode',None)
        obj.bond_class          = convert('bondclass',
                                          bc,
                                          curncy=ccy,
                                          country=country,
                                          **bck)
        
        obj.multiplier = self.safefloat(multiplier,0.01)
        obj.settlement_delay = self.safeint(settlement_delay,3)
        if commit:
            obj.save()
        return obj

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

