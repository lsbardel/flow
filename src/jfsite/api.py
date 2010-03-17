from django.conf.urls.defaults import *
 
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
 
from jflow.db.instdata import api as dataapi
 
auth = HttpBasicAuthentication(realm='JFLOW API')
 
urlpatterns = patterns('',
    *dataapi.urls(auth)
)