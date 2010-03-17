from djcms.views import Factory

from jflow.site.views import loadcsv

import search
import display
import edit
import add
import cloud

class loadview(loadcsv.view):
    datatype   = 'instrument'
    authflag   = 'add'
        
class loadhistoryview(loadcsv.view):
    datatype   = 'tseries'
    authflag   = 'add'
    
    def title(self):
        return "Load Historical data into database"


class view(Factory.view):
    default_view = 'search'
    
    search = Factory.child('search', 'search', search.view)
    view   = Factory.child('view', 'view', display.view, robj=True)
    edit   = Factory.child('edit', 'edit', edit.view, robj=True)
    add    = Factory.child('add',  'add new data', add.view)
    load   = Factory.child('load', 'load data IDs', loadview)
    hist   = Factory.child('hist', 'load data history', loadhistoryview)
    cloud  = Factory.child('cloud', 'label cloud', cloud.view, in_nav = False)
    