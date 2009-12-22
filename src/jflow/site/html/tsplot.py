from djpcms.html import htmlPlugin

class tsplot(htmlPlugin):
    tag = 'div'
    
    def __init__(self, height = '400px', code = None, **kwargs):
        self.attr(style = 'height:%s' % height)
        self.addclass('ts-plot-module')
        if code:
            htmlPlugin(tag = 'code', inner = code).attr(style = 'display: none').appendTo(self)
    
    def wrap_internal_widget(self, el):
        return el