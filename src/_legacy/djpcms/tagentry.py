from djpcms.html import htmlPlugin, searchentry, link

class entry(searchentry):
    '''
    HTML plug-in which render a search result
    '''
    def __init__(self, **kwargs):
        if not self.template:
            self.template = 'jflow/components/tagged-entry.html'
        super(entry,self).__init__(**kwargs)
    
    def labels(self):
        tags = self.object.tags.split(' ')
        if tags:
            sview   = self.view.newchildview('search')
            url     = sview.url
            tgs     = htmlPlugin(tag = 'p')
            for t in tags:
                if tgs:
                    tgs.append(', ')
                tgs.append(link(url = sview.tagurlmaker(url,t), inner = t))
            return tgs.render()