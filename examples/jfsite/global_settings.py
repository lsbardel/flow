import os
local_dir = os.path.split(os.path.abspath(__file__))[0]

RPC_SERVER_PORT = 9010
    
ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   'sqlite3',
        'NAME':     'testdb.sqlite'
    }
}

TIME_ZONE             = 'Europe/London'
LANGUAGE_CODE         = 'en-gb'
SITE_ID = 1
USE_I18N = False

DATE_FORMAT            = 'D d M y'
DATETIME_FORMAT        = 'D d M y P'
SECRET_KEY             = ')0!7rr*cs-7^4)5$@bjtxf_xlwy2b!n_wh2lm71pt^#in7^5t2'


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

INSTALLED_APPS = [
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
    #'djpcms.contrib.admin',
    'django.contrib.admin',
    'tagging',
    'flowrepo',
    'dynts',
    #
    'extracontent',
    'ccy.basket',
    'jflow.db.portfolio',
    'jflow.db.instdata',
    'jflow.db.trade',
    'jflow.web',
    #
    #'south'
]


# DJPCMS SETTINGS
TEMPLATE_DIRS       = (os.path.join(local_dir, 'templates'),)
MEDIA_ROOT          = os.path.join(local_dir, 'media')
MEDIA_URL           = '/media/'
ADMIN_MEDIA_PREFIX  = MEDIA_URL + 'admin/'
DJPCMS_STYLE        = 'redmond'
USER_ACCOUNT_HOME_URL  = '/accounts/'
LOGIN_URL  = '%slogin/' % USER_ACCOUNT_HOME_URL
LOGOUT_URL = '%slogout/' % USER_ACCOUNT_HOME_URL
DJPCMS_PLUGINS  = ['djpcms.plugins.*',
                   'djpcms.views.apps.tagging.plugins',
                   'flowrepo.cms',
                   'dynts.web.plugins',
                   'jflow.web.plugins.*']
ROOT_URLCONF            = 'jfsite.urls'
APPLICATION_URL_MODULE  = 'jfsite.appurls'

