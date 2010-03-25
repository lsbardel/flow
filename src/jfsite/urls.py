from djpcms.urls import *
from djpcms.contrib.admin import autocomplete
from jflow.db.instdata.models import DataId

autocomplete.register(DataId,['code','name'])

api_urls = r'^api/', include('jfsite.api')
 
urlpatterns = patterns('', api_urls, *site_urls)

