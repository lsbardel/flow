
import os
import packages
os.environ['JFLOW_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.release'
os.environ['STDNET_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.release'
PSETTINGS = packages.install()

if not PSETTINGS.dev:
    os.environ['PYTHON_EGG_CACHE'] = PSETTINGS.egg_cache

DEBUG = PSETTINGS.debug
TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'jflow.db.testrunner.JflowTestSuiteRunner'
    

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)


MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   PSETTINGS.dbengine,
        'NAME':     PSETTINGS.dbname,
        'USER':     PSETTINGS.dbuser,
        'PASSWORD': PSETTINGS.dbpassword,
        'HOST':     PSETTINGS.dbhost,
        'PORT':     PSETTINGS.dbport,
    }
}

CACHE_BACKEND     = PSETTINGS.cache

TIME_ZONE             = 'Europe/London'
LANGUAGE_CODE         = 'en-gb'
SITE_ID = 1
USE_I18N = False

DATE_FORMAT            = 'D d M y'
DATETIME_FORMAT        = 'D d M y P'
SERVE_STATIC_FILES     = PSETTINGS.servs
MEDIA_ROOT             = PSETTINGS.media_root()
MEDIA_URL              = '/media/'
ADMIN_MEDIA_PREFIX     = MEDIA_URL + 'django_admin/'
SECRET_KEY             = PSETTINGS.id.SECRET_KEY
ADMIN_URL_PREFIX       = PSETTINGS.id.ADMIN_URL_PREFIX
 
USER_ACCOUNT_HOME_URL  = '/accounts/'
LOGIN_URL  = '%slogin/' % USER_ACCOUNT_HOME_URL
LOGOUT_URL = '%slogout/' % USER_ACCOUNT_HOME_URL

# EMAILS
SEND_BROKEN_LINK_EMAILS = True
EMAIL_HOST             = PSETTINGS.id.EMAIL_HOST
EMAIL_PORT             = PSETTINGS.id.EMAIL_PORT
EMAIL_SUBJECT_PREFIX   = PSETTINGS.id.EMAIL_SUBJECT_PREFIX
EMAIL_HOST_USER        = PSETTINGS.id.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD    = PSETTINGS.id.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS          = PSETTINGS.id.EMAIL_USE_TLS
DEFAULT_FROM_EMAIL     = PSETTINGS.id.DEFAULT_FROM_EMAIL


ROOT_URLCONF = 'jfsite.urls'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "djpcms.core.context_processors.djpcms",
)

TEMPLATE_DIRS     = (os.path.join(PSETTINGS.LOCDIR, 'templates'))

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.markup',
    #
    'djpcms',
    'djpcms.contrib.admin',
    #'django.contrib.admin',
    #'djpcms.contrib.compressor',
    'tagging',
    'flowrepo',
    #
    'ccy.basket',
    'jflow',
    'jflow.db.instdata',
    'jflow.db.trade',
    'unuk.contrib.txdo',
    #
    #'south'
)

LEAH_SERVER_URL = PSETTINGS.leahurl

COMPRESS = True
# DJPCMS SETTINGS
DJPCMS_PLUGINS  = ['djpcms.plugins.*',
                   'djpcms.views.apps.tagging.plugins',
                   'flowrepo.cms',
                   'jfsite.cms.plugins.*',
                   'jfsite.applications.trade']
GOOGLE_ANALYTICS_ID     = PSETTINGS.id.GOOGLE_ANALYTICS_ID
APPLICATION_URL_MODULE  = 'jfsite.appurls'
GRID960_DEFAULT_FIXED   = True
