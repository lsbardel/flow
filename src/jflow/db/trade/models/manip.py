import datetime

from django.db import connection
from django.db.models import Q

from trade import *
from managers import *

__all__ = ['Position',
           'PositionHistory',
           'ProfitAndLoss']




class Position(TimeStamp):
    '''
    Financial Instrument position
    '''
    instrumentCode   = models.ForeignKey('instdata.InstrumentCode')
    custodian        = models.ForeignKey(CustodyAccount)
    fund             = models.ForeignKey(Fund)
    status           = models.IntegerField(default=1, choices = position_status_choice)
    open_date        = models.DateField(blank = False)
    close_date       = models.DateField(blank = True, null = True)
    
    objects = PositionManager()    
    
    class Meta:
        app_label    = current_app_label
        ordering = ('open_date','instrumentCode')
        unique_together = (('open_date', 'fund', 'custodian', 'instrumentCode'),)
        
    def __unicode__(self):
        return u'%s (%s)' % (self.instrumentCode,self.fund)
    
    def instrument(self):
        return self.instrumentCode.instrument()
    
    def get_description(self):
        return self.instrument().description()
        
    def __get_history(self):
        return PositionHistory.objects.filter(position = self)
    
    def end_date(self):
        return self.instrumentCode.end_date()
    
    def __get_code(self):
        return self.instrumentCode.code
    code = property(fget = __get_code)
    
    def history(self):
        '''
        Get position history
        Uses the jflow.core.dates library
        '''
        from jflow.core import dates
        ts = dates.dateserie()
        hist = self.__get_history()
        for h in hist:
            ts.add(h.dt,h)
        return ts
    
    def at(self, dte = None):
        if dte == None:
            dte = datetime.date.today()
        hist = self.history()
        idx  = hist.index(dte)
        i0   = idx[0]
        try:
            kv = hist[i0]
            if kv.key <= dte:
                return kv.value
            else: 
                return None
        except:
            return None
        
    def first_at_or_before(self, dte = None):
        if dte == None:
            dte = datetime.date.today()
        hist = self.__get_history().filter(dt__lte = dte)
        if hist.count():
            return hist[0]
        else:
            return None
    
    def clear(self):
        ph = self.__get_history()
        for p in ph:
            p.delete()
    
    @staticmethod
    def get_last_modified():
        try:
            p = Position.objects.latest('last_modified')
            return p.last_modified
        except:
            return datetime.date.min
        
    def getposition(self, dte):
        phist = PositionHistory.objects.filter(position = self, dt__lte = dte)
        C     = phist.count()
        if C == 0:
            return None
        h = phist[C-1]
        return self.make_position(size           = h.size,
                                  value          = h.value,
                                  dirty_value    = h.dirty_value,
                                  book_cost_base = h.book_cost_base,
                                  cost_unit_base = h.cost_unit_base,
                                  dt             = h.dt,
                                  curdt          = dte)
    
    def make_position(self, size = 0, value = 0, dirty_value = None,
                      book_cost_base = None, cost_unit_base = None,
                      dt = None, curdt = None):
        from jflow.core.finins import holding
        inst        = self.instrument()
        sizf        = float(size)
        h           = holding(size, value/sizf, dirty_value, cost_unit_base, book_cost_base, dt)
        return inst.make_position(id              = self.id,
                                  details         = h,
                                  open_date       = self.open_date,
                                  calc_date       = curdt,
                                  dbobj           = self)
    

     
            
class PositionHistory(TimeStamp):
    position       = models.ForeignKey(Position)
    dt             = models.DateField(verbose_name = 'date')
    pl             = models.ForeignKey('ProfitAndLoss', null = True, blank = True, editable = False)
    size           = models.DecimalField(default = 0, max_digits=MAX_DIGITS, decimal_places = ROUNDING)
    value          = models.FloatField(default = 0.0)
    dirty_value    = models.FloatField(default = 0.0)
    cost_unit_base = models.FloatField(default = 0.0)
    book_cost_base = models.FloatField(default = 0.0)
    
    objects = PositionHistoryManager()
    
    class Meta:
        app_label       = current_app_label
        ordering        = ('position','-dt')
        get_latest_by   = "dt"
        unique_together = (("position", "dt"),)
        verbose_name_plural = 'Position Histories'
        
    def __unicode__(self):
        return '%s -- %s -- size: %s' % (self.dt,self.position,self.size)
        
    def delete(self):
        pl = self.pl
        if pl:
            pl.delete()
        super(PositionHistory,self).delete()
        

class ProfitAndLoss(models.Model):
    pl   = models.FloatField(default = 0.0)
    dv01 = models.FloatField(default = 0.0)
    
    class Meta:
        app_label    = current_app_label
