from djpcms.settings import HTML_CLASSES
from djpcms.html import form, formlet, submit, div

from fields import ShortAddForm

__all__ = ['shortaddform']

class shortaddform(form):
    
    def __init__(self, *args, **attrs):
        super(shortaddform,self).__init__(*args, **attrs)
        self.addclass(HTML_CLASSES.ajax_form)
        
    def _make(self, data = None, **kwargs):
        co  = self.make_container(div)
        co['addform'] = formlet(form     = ShortAddForm,
                                data     = data,
                                instance = self.object,
                                submit   = submit(name='add_short', value="Add"))
