from djpcms.views.tagging.html import tagsave

import add

class view(add.view):
    authflag    = 'change'
    '''
     Add new data id to database.
     If the data id is a financial instrument, a new
     instrument will be also added to the database.
    '''
    def title(self):
        return 'Editing %s' % self.object
    
    def edit_labels(self, params):
        tagsave(params, self.object)