from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from models import PortfolioDisplay, PortfolioDisplayElement

def jsondisplays():
    di = {'elements': PortfolioDisplayElement.objects.tojson(),
          'choices':  PortfolioDisplay.objects.tojson()}
    vd = simplejson.dumps(di)
    return mark_safe(force_unicode(vd))
            
            
    