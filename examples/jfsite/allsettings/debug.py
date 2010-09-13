from jfsite.allsettings.release import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_BACKEND    = 'redis://127.0.0.1:6379/?db=6'
NUM_PROCESSES_PER_CPU = 0