from jflow.jfsite.global_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
CACHE_BACKEND      = 'memcached://localhost:11211/'
DEFAULT_BACKEND    = 'redis://127.0.0.1:6379/?db=7'
#DEFAULT_BACKEND    = 'couchdb://127.0.0.1/?db=test'