import datetime

from base import *
from data import BaseModel
from instrument import InstrumentCode

class DecompManager(models.Manager):
    
    def forobject(self, inst):
        if not isinstance(inst,InstrumentCode):
            return None
        else:
            v = self.filter(instrument = inst)
            if v:
                return v[0].composition()
            else:
                return None


class InstDecomp(BaseModel):
    instrument = models.ForeignKey(InstrumentCode)
    
    objects = DecompManager()
    
    def composition(self, dt = None):
        c = self.instdecomphistory_set.latest()
        if c:
            co = c.composition
            return co.replace(' ','').replace('\r','').replace('\n','')
        else:
            return None
        
    def add(self, comp, dt = None):
        dt = dt or datetime.date.today()
        hh = self.instdecomphistory_set.filter(dt = dt)
        comp = comp or ""
        if hh:
            h = hh[0]
            h.composition = comp
        else:
            h = InstDecompHistory(inst_decomp = self,
                                  dt = dt,
                                  composition = comp)
        h.save()
        return h
    
    class Meta:
        verbose_name = 'Instrument Decomp'
        app_label    = current_app_label        


class InstDecompHistory(models.Model):
    inst_decomp  = models.ForeignKey(InstDecomp,verbose_name='decomposition')
    dt           = models.DateField(verbose_name='date')
    composition  = models.TextField()
    
    def __unicode__(self):
        return self.composition
    
    def __get_instrument(self):
        return self.inst_decomp.instrument
    instrument = property(fget = __get_instrument)
    
    
    class Meta:
        verbose_name = 'Instrument Decomp History'
        verbose_name_plural = 'Instrument Decomp Histories'
        ordering        = ['-dt']
        unique_together = (('inst_decomp','dt'),)
        get_latest_by   = 'dt'
        app_label       = current_app_label