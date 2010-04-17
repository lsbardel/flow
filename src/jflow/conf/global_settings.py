import logging

LIVE_CALCULATION = False

LOGGING_VERBOSE = 2
LOGGING_LEVEL   = logging.INFO
LOGGING_PREFIX  = '' 

DAYS_BACK = 60

MAX_RATE_LOADING_THREADS = 3

CACHE_BACKEND = 'dummy://'

RATE_CACHE_SECONDS      = 10*24*60*60   # 10 days
PORTFOLIO_CACHE_SECONDS = 10*60*60      # 10 hours

DATE_FORMAT = 'D d M y'

FIRM_CODE_NAME = 'Firm code'

FIELDS_SHORTCUTS = {'ASK' :'ASK_PRICE',
                    'BID' :'BID_PRICE',
                    'LOW' :'LOW_PRICE',
                    'HIGH':'HIGH_PRICE',
                    'OPEN':'OPEN_PRICE',
                    'CLOSE':'LAST_PRICE',
                    'LAST':'LAST_PRICE'}

DEFAULT_VENDOR_FOR_SITE = 'YAHOO'
DEFAULT_DATA_FIELD = 'LAST_PRICE'
VENDOR_MODULE = 'jflow.vendors'

BADVALUE = 9999999
