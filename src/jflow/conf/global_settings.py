import logging

LIVE_CALCULATION = False

LOGGING_LEVEL   = logging.INFO
if logging.thread:
    LOGGING_FORMAT = "%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s"
else:
    LOGGING_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOGGING_HANDLERS = 'TimedRotatingFileHandler:midnight'
LOGGING_PREFIX  = '' 

DAYS_BACK = 60

MAX_RATE_LOADING_THREADS = 3

PORTFOLIO_CACHE_BACKEND = None

RATE_CACHE_SECONDS      = 10*24*60*60   # 10 days
PORTFOLIO_CACHE_SECONDS = 10*60*60      # 10 hours

FIRM_CODE_NAME = 'Firm code'

FIELDS_SHORTCUTS = {'ASK' :'ASK_PRICE',
                    'BID' :'BID_PRICE',
                    'LOW' :'LOW_PRICE',
                    'HIGH':'HIGH_PRICE',
                    'OPEN':'OPEN_PRICE',
                    'CLOSE':'LAST_PRICE',
                    'LAST':'LAST_PRICE'}

DEFAULT_TRADING_CENTRES = 'LON,NY,TGT'
DEFAULT_VENDOR_FOR_SITE = 'YAHOO'
DEFAULT_DATA_FIELD = 'LAST_PRICE'
VENDOR_MODULE = 'jflow.vendors'

BADVALUE = 9999999

TRIM_STRING_CODE = lambda x: x.upper()
