from django.db import models


class PeopleData(models.Model):
    trader          = models.OneToOneField('trade.Trader')
    default_fund    = models.ForeignKey('trade.Fund')
    default_history = models.PositiveIntegerField(default = 12)
    
    def __get_user(self):
        return self.trader.user
    user = property(fget = __get_user)
    
    def __get_team(self):
        return self.trader.fund_holder
    team = property(fget = __get_team)
    
    def __unicode__(self):
        return u'%s' % self.trader
    
    def __get_preference(self):
        return self.trader
    preference = property(fget = __get_preference)
    

       

class UserPortfolioView(models.Model):
    user = models.ForeignKey('auth.User')
    view = models.OneToOneField('trade.PortfolioView')
    default = models.BooleanField(default = False)
    
    def __unicode__(self):
        return '%s - %s' % (self.view,self.user)
    
    def shortdes(self):
        return '%s(%s)' % (self.view.name,self.user)
    
       
    