from django.conf import settings

VERSION = '0.1'
from django.contrib.sites.models import Site

try:
    s    = Site.objects.get_current()
    url  = s.domain
    name = s.name
except:
    url  = ''
    name = ''


FEED_AGGREGATOR_AGENT = getattr(settings,
                                'FEED_AGGREGATOR_AGENT',
                                'joinfeed %s - %s' % (VERSION, url))

FEED_AGGREGATOR_TITLE = getattr(settings,
                                'FEED_AGGREGATOR_TITLE',
                                '%s aggregator' % name)