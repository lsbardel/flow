from urllib2 import URLError

from django import template
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def server_info(cl,code):
    """
    Returns the string contained in the setting MEDIA_URL
    """
    from jflow.db.utility.server import userproxyserver
    serv = userproxyserver(cl.request.user)
    html = ''
    error_class = "error-message"
    if serv:
        try:
            blbconnections = serv.numservers(code)
            if blbconnections:
                html = '<p><b> %s Bloomberg servers available </b></p>' % blbconnections
            else:
                html = '<p class="%s"><b> No Bloomberg servers available </b></p>' % error_class
        except URLError:
            html = '<p class="%s"><b> Prospero dataserver not available </b></p>' % error_class
        except Exception, e:
            html = '<p class="%s"><b> %s </b></p>' % (error_class,e)
    else:
        html = '<p class="%s"><b> Prospero dataserver not available </b><p>' % error_class
    
    return mark_safe(force_unicode(html))