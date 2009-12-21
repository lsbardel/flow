from jflow.db.instdata.settings import *

DAYS_BACK = 60
LIVE_CALCULATION = False

LOGGING_VERBOSE = getattr(settings,'LOGGING_VERBOSE',2)
SERVER_LOGGER_MODULE = getattr(settings, 'SERVER_LOGGER_MODULE', None)