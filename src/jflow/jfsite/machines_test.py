
from djpcms.utils.machines import machine, get_machine

class SiteMachine(machine):

    def __init__(self,
                 dbengine   = 'sqlite3',
                 dbname     = 'jflowdb.sqlite',
                 cache      = 'memcached://127.0.0.1:11211/',
                 leahurl    = 'http://localhost:8010',
                  **kwargs):
        super(SiteMachine,self).__init__(dbengine = dbengine,
                                         dbname = dbname,
                                         cache = cache,
                                         **kwargs)
        self.leahurl = leahurl


SiteMachine(debug = False)
SiteMachine(name  = 'flow',
            dev   = True,
            debug = True,
            servs = True)


class Identity(object):

    def __init__(self):
        self.SECRET_KEY          = ')0!7rr*cs-7^4)5$@bjtxf_xlwy2b!n_wh2lm71pt^#in7^5t2'
        self.ADMIN_URL_PREFIX    = '/admin/'
        self.GOOGLE_ANALYTICS_ID = None
        
        #email
        self.EMAIL_USE_TLS         = True
        self.EMAIL_HOST            = None
        self.EMAIL_PORT            = 587
        self.EMAIL_SUBJECT_PREFIX  = '[jflow] '
        self.EMAIL_HOST_PASSWORD   = None
        self.EMAIL_HOST_USER       = None
        self.DEFAULT_FROM_EMAIL    = None

