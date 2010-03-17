from django.contrib.contenttypes.models import ContentType
from django.db import models

from tagging.managers import ModelTaggedItemManager

from jflow.db.instdata.converters import convert
from jflow.db.instdata.settings import DEFAULT_VENDOR_FOR_SITE


class DataIdManager(ModelTaggedItemManager):
    
    def ct_from_type(self, type):
        app_label = self.model._meta.app_label
        return ContentType.objects.get(name = type, app_label = app_label)
    
    def for_type(self, type):
        try:
            ct = self.ct_from_type(type)
        except:
            return self.none()
        return self.filter(content_type = ct)
    
    def get_or_create(self, **kwargs):
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
        vend = kwargs.pop('default_vendor',DEFAULT_VENDOR_FOR_SITE)
        dfv  = convert('vendor', vend)
        if not code:
            raise ValueError('cannot add data id, code not specified')
        type = kwargs.pop('type',None)
        if type == 'future':
            return
        else:
            country = kwargs.pop('country',None)
        
        if not country:
            raise ValueError('Country not specified')
        
        tags = kwargs.pop('tags','')
        id, created = super(DataIdManager,self).get_or_create(code = code)
        id.country = convert('country', country)
        id.default_vendor = dfv
        
        inst = None
        if not created:
            inst = id.instrument
        if type:
            try:
                ct = self.ct_from_type(type)
            except:
                raise ValueError('Data type %s not available' % type)
            model = ct.model_class()
            opts  = model._meta
            if inst:
                if inst._meta.model != model:
                    inst.delete()
                    inst = None
            if not inst:
                inst = model(dataid = id, code = id.code)
            for key,val in kwargs.items():
                try:
                    field = opts.get_field_by_name(key)
                except:
                    continue
                val = convert(key, val)
                setattr(inst,key,val)
            inst.save()
            id.curncy = inst.ccy()
            iid = inst.id
        else:
            if inst:
                inst.delete()
            ct = None
            iid = 0

        id.content_type = ct
        id.object_id    = iid
        id.save()
        return id,created
        
class InstrumentManager(models.Manager):
    pass

class DecompManager(models.Manager):
    
    def for_object(self, id, code = None, dt = None):
        code = code or id.code
        v = self.filter(dataid = id, code = code)
        if not dt:
            v = v.latest
        return v.composition
        