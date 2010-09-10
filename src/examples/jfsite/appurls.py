from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.views import appsite
from djpcms.views.apps.user import UserApplication
from djpcms.views.apps.tagging import Tag, TagsApplication
from djpcms.views.apps.memcache import MemcacheApplication

from jflow.db.instdata.models import DataId
from flowrepo.models import Report, FlowItem

from jflow.jfsite.cms.applications import data


appsite.site.register('/tagging/', TagsApplication, model = Tag)
    
#___________________________________ REGISTERING DYNAMIC APPLICATIONS
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
appsite.site.register('/data/', data.DataApplication, model = DataId)
appsite.site.register('/econometric/', data.EconometricApplication,  model = data.EconometricAnalysis)
appsite.site.register('/report/', data.BlogApplication, model = Report)
#appsite.site.register('/items/', data.FlowItemApplication, model = FlowItem)
appsite.site.register('/memcached/', MemcacheApplication)


if 'jflow.db.trade' in settings.INSTALLED_APPS:
    from jflow.jfsite.cms.applications import trade
    appsite.site.register('/team/', trade.FundHolderApplication, model = trade.FundHolder)
    appsite.site.register('/portfolioview/', trade.PortfolioViewApplication, model = trade.PortfolioView)
    appsite.site.register('/portfolio/', trade.FundApplication, model = trade.Fund)
    appsite.site.register('/manual-trade/', trade.ManualTradeApplication, model = trade.ManualTrade)


    

