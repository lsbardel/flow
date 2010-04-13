
import json


__all__ = ['jsonbase', 'jsonwrap', 'json']

    
class jsonbase(object):

    def dict(self):
        pass

    def _dump(self, elem):
        '''
        Use JSON to serialize elem
        '''
        return json.dumps(elem)
    
    def dumps(self):
        return self._dump(self.dict())
    
    def tojson(self):
        from django.utils.safestring import mark_safe
        return mark_safe(u'%s' % self.dumps())
    
    
class jsonwrap(jsonbase):
    
    def __init__(self, data = None, type = None):
        self.data = data
        self.type = type
    
    def dict(self):
        return {'data': self.data,
                'type': self.type}
        
        