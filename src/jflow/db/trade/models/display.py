import datetime

from base import *
from formatters import formatter_tuple, formatter_default


__all__ = ['PortfolioDisplay',
           'PortfolioDisplayElement',
           'PortfolioDisplayComponent']

            
class PortfolioDisplayManager(models.Manager):
    
    def tojson(self):
        objs = self.all()
        js = []
        for o in objs:
            js.append(o.tojson())
        return js
    
    def get_last_modified(self):
        try:
            p = self.latest('last_modified')
            return p.last_modified
        except:
            return datetime.date.min
    

#class PortfolioDisplay(CodeDescriptionModel):
class PortfolioDisplay(CodeDescriptionModelTS):
    '''
    Model for a portfolio display configuration
    '''
    
    objects = PortfolioDisplayManager()
    
    def display(self):
        els = self.portfoliodisplaycomponent_set.all()
        pr = ''
        re = ''
        for el in els:
            re += pr + el.code()
            pr  = ', '
        return re            
    
    class Meta:
        app_label = current_app_label
        ordering  = ('code',)
        
    def tojson(self):
        json = super(PortfolioDisplay,self).tojson()
        vals = []
        json['values'] = vals
        els = self.portfoliodisplaycomponent_set.all()
        for e in els:
            vals.append(e.element.code)
        return json
       
        
class PortfolioDisplayElement(CodeDescriptionModel):
    '''
    A portfolio display element
    '''
    formatter = models.CharField(max_length = 22,
                                 default = formatter_default,
                                 choices = formatter_tuple,
                                 blank = True,
                                 null = True)
    sortable  = models.BooleanField(default = True)
    order     = models.IntegerField(default = 9999)
    dynamic   = models.BooleanField(default = False)
    
    objects = PortfolioDisplayManager()
    
    class Meta:
        app_label = current_app_label
        ordering  = ('order',)
        
    def tojson(self):
        return {'code': self.code,
                'name': self.name,
                'description': self.description,
                'formatter': self.formatter}


class PortfolioDisplayComponent(models.Model):
    element     = models.ForeignKey(PortfolioDisplayElement)
    view        = models.ForeignKey(PortfolioDisplay)
    
    class Meta:
        app_label = current_app_label
        ordering  = ('view','element',)
        
    def code(self):
        return self.element.code
    
    def name(self):
        return self.element.name
    
    def description(self):
        return self.element.description
   