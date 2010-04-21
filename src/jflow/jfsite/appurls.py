from django.contrib.auth.models import User
from django import http
from django.forms.models import modelform_factory

from djpcms.conf import settings
from djpcms.utils.html import autocomplete
from djpcms.views import appsite
from djpcms.views.user import UserApplication
from djpcms.views.apps.memcache import MemcacheApplication

from jflow.db.instdata.models import DataId

autocomplete.register(DataId,['code','name'])
autocomplete.register(User,['username','username'])


from jflow.jfsite import applications
    
#___________________________________ REGISTERING DYNAMIC APPLICATIONS
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
appsite.site.register('/data/',
                      applications.DataApplication,
                      model = applications.DataId)
appsite.site.register('/econometric/',
                      applications.EconometricApplication,
                      model = applications.EconometricAnalysis)
appsite.site.register('/memcached/', MemcacheApplication)

if 'flowrepo' in settings.INSTALLED_APPS:
    appsite.site.register('/report/', applications.BlogApplication, model = applications.Report)

