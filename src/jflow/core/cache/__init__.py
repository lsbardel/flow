from cgi import parse_qsl

from jflow.conf import settings
from stdnet.main import get_cache

BACKENDS = {
    'memcached': 'memcached',
    'locmem': 'locmem',
    'file': 'filebased',
    'db': 'db',
    'dummy': 'dummy',
}

cache = get_cache(settings.CACHE_BACKEND)
