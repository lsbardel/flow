from djpcms.urls import *

api_urls = r'^api/', include('jfsite.api')
 
urlpatterns = patterns('', api_urls, *site_urls)

