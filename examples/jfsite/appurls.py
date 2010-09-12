from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.views import appsite
from djpcms.views.apps.user import UserApplication
from djpcms.views.apps.tagging import Tag, TagsApplication
from djpcms.views.apps.memcache import MemcacheApplication

from jflow.db.instdata.models import DataId
from jflow.db.netdata.models import ServerMachine
from flowrepo.models import Report, FlowItem
from flowrepo.cms import FlowItemApplication, ReportApplication

from jflow.web.applications import data

from jfsite.forms import ReportForm


class BlogApplication(ReportApplication):
    form_ajax = False
    inherit   = True
    _form_save       = 'save'
    _form_continue   = 'save and continue'
    name      = 'report'
    form      = ReportForm
    
    class Media:
        css = {
            'all': ('flowrepo/flowrepo.css',)
        }

class ItemApplication(FlowItemApplication):
    name      = 'items'
    



appsite.site.register('/tagging/', TagsApplication, model = Tag)
    
#___________________________________ REGISTERING DYNAMIC APPLICATIONS
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
appsite.site.register('/data/', data.DataApplication, model = DataId)
appsite.site.register('/econometric/', data.EconometricApplication,  model = data.EconometricAnalysis)
appsite.site.register('/report/', BlogApplication, model = Report)
appsite.site.register('/servers/', data.ServerApplication, model = ServerMachine)
#appsite.site.register('/items/', FlowItemApplication, model = FlowItem)


if 'jflow.db.trade' in settings.INSTALLED_APPS:
    from jflow.web.applications import trade
    appsite.site.register('/team/', trade.FundHolderApplication, model = trade.FundHolder)
    appsite.site.register('/portfolioview/', trade.PortfolioViewApplication, model = trade.PortfolioView)
    appsite.site.register('/portfolio/', trade.FundApplication, model = trade.Fund)
    appsite.site.register('/manual-trade/', trade.ManualTradeApplication, model = trade.ManualTrade)


    

