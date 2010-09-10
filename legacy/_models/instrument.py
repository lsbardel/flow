import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from interface import InstrumentInterface
import factory as FACTORY
from base import *


__all__ = ['InstrumentCode',
           'FincialInstrumentBase',
           'NoDataInstrumentBase']


class InstrumentCodeManager(models.Manager):
    
    def formodel(self, model, **kwargs):
        if model == None:
            raise ValueError, 'No Instrument model selected'
        try:
            m = model()
            model_name = m._meta.module_name
        except:
            model_name = str(model)
        ct = ContentType.objects.get(app_label = current_app_label,
                                     model = model_name)
        return self.filter(content_type = ct, **kwargs)
        
    def cleanmissing(self):
        ics = self.all()
        cl = 0
        for ic in ics:
            inst = ic.instrument()
            if inst == None:
                cl += 1
                ic.delete()
        return cl


class InstrumentCode(InstrumentInterface):
    '''
    A table which relate an instrument code with an instrument table
    '''
    code          = models.CharField(unique=True, max_length=32)
    firm_code     = models.CharField(blank=True,
                                     max_length=50,
                                     verbose_name = settings.FIRM_CODE_NAME)
    content_type  = models.ForeignKey(ContentType, blank=True, null=True)
    data_id       = models.ForeignKey('dataid', blank = True, null = True)
    
    objects       = InstrumentCodeManager()
    
    class Meta:
        app_label    = current_app_label
        ordering     = ('code',)
        verbose_name = "Instrument"
        
    def __unicode__(self):
        return u'%s' % self.code
    
    def delete(self):
        inst = self.instrument()
        if inst:
            inst.delete()
        super(InstrumentCode,self).delete()
    
    @lazyattr
    def instrument(self):
        try:
            inst = self.content_type.get_object_for_this_type(id=self.id)
            inst._code = self
            return inst
        except:
            return None
        
    def delete_instrument(self):
        inst = self.instrument()
        if inst:
            inst.delete()
        
    def delete(self):
        self.delete_instrument()
        super(InstrumentCode,self).delete()
    
    def __get_type(self):
        inst = self.instrument()
        if inst:
            return inst._meta.module_name
        else:
            return None
    instype = property(fget = __get_type)
    
    def __get_instclass(self):
        inst = self.instrument()
        if inst:
            return inst.__class__
        else:
            return None
    insclass = property(fget = __get_instclass)
    
    def ccy(self):
        return self.instrument().ccy()
    
    def end_date(self):
        return self.instrument().end_date()
    
    def live(self):
        return self.instrument().live()
    
    def data_link(self):
        return self.instrument().data_link()
    
    def description(self):
        return self.instrument().description()
    
    def isotc(self):
        return self.instrument().isotc()
    
    def tags(self):
        if self.data_id:
            return str(self.data_id.tags)
        else:
            return ''
        
    def get_underlying(self):
        return self.instrument().get_underlying()
    
    def infodict(self):
        inst = self.instrument()
        return inst.infodict()
    
    def tojson(self):
        inst = self.instrument()
        return inst.tojson()
    
        
        
class FincialInstrumentBase(InstrumentInterface):
    '''
    Base Abstract class for Financial Instruments
    '''
    id  = models.IntegerField(primary_key = True)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return u'%s' % self.code
    
    def has_firm_code(self):
        return True
    
    #def __get_code(self):
    #    if not hasattr(self,'_code'):
    #        self.__check()
    #    return self._code
    #code = property(fget = __get_code)
    
    def __get_data_id(self):
        return self.code.data_id
    data_id = property(fget = __get_data_id)
    
    def firm_code(self):
        return self._code.firm_code
    #firm_code.short_description = settings.FIRM_CODE_NAME
    
    def tags(self):
        return self._code.tags()
    
    def make_position(self, **kwargs):
        '''
        Create a financial instrument
        '''
        raise NotImplementedError, 'Cannot build position for %s. Function not implemented' % self
    
    def check(self):
        if not hasattr(self,'_code'):
            return self.__check()
        else:
            return True
    
    def _check_id(self):
        id = self.data_id
        if not id:
            self.code.delete()
            return False
        #dr = id.dates_range
        #if not dr:
        #    from prospero.contrib.data.models import DateRange
        #    dr = self.GetDateRange()
        #    dr.save()
        #    id.dates_range = dr
        #    id.save()
        #    id.live_at_date()
        return True
    
    def get_instrumentCode(self):
        return InstrumentCode.objects.get(id = self.id)
    
    def __check(self):
        try:
            ic = InstrumentCode.objects.get(id = self.id)
            self._code = ic
            return True
        except:
            self.delete()
            return False
        

class NoDataInstrumentBase(FincialInstrumentBase):
    has_data_id       = False
    
    class Meta:
        abstract = True
        
    def _check_id(self):
        return True