from django.conf.urls.defaults import *
 
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
 
from jflow.db.instdata import api as dataapi
from jflow.db.trade import api as tradeapi
 
auth = HttpBasicAuthentication(realm='JFLOW API')
 
apis = dataapi.urls(auth) + tradeapi.urls(auth)

urlpatterns = patterns('', *apis)