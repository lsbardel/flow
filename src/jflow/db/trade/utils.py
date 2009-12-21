from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from models import PortfolioDisplay, PortfolioDisplayElement

def jsondisplays():
    di = {'elements': PortfolioDisplayElement.objects.tojson(),
          'choices':  PortfolioDisplay.objects.tojson()}
    vd = simplejson.dumps(di)
    return mark_safe(force_unicode(vd))
            
            

def get_object_id(obj):
    '''
    Given an object instance it return a unique id across all models
    '''
    opt = obj._meta
    ct = ContentType.objects.get_for_model(obj)
    return '%s_%s' % (ct.id,obj.id)

def get_object_from_id(id):
    try:
        ids = str(id).split('_')
        ct = ContentType.objects.get_for_id(int(ids[0]))
        return ct.get_object_for_this_type(id = int(ids[1]))
    except:
        return None