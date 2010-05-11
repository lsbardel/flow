from django import forms
from django.template import loader

from djpcms.utils import mark_safe
from djpcms.plugins import DJPplugin
from djpcms.views import appsite

from jflow.conf import settings 
from jflow.db.trade.models import FundHolder, Fund, PortfolioView


class TeamPosition(DJPplugin):
    '''Display the position of a team base on some inputs specified by the plugin form 
    '''
    class Media:
        js = ['txdo/JSON.js',
              'txdo/Orbited.js',
              'txdo/protocol/stomp.js']
        
    def render(self, djp, wrapper, prefix, height = 400, **kwargs):
        pass