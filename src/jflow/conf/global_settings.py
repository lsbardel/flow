LIVE_CALCULATION = False

LOGGING_VERBOSE = 2

DAYS_BACK = 60

MAX_RATE_LOADING_THREADS = 3

CACHE_BACKEND = 'dummy://'

SERVER_LOGGER_MODULE = None

DATE_FORMAT = 'D d M y'

FIRM_CODE_NAME = 'Firm code'

FIELDS_SHORTCUTS = {'ASK' :'ASK_PRICE',
                    'BID' :'BID_PRICE',
                    'LOW' :'LOW_PRICE',
                    'HIGH':'HIGH_PRICE',
                    'OPEN':'OPEN_PRICE'}

DEFAULT_VENDOR_FOR_SITE = 'GOOGLE'
DEFAULT_DATA_FIELD = 'LAST_PRICE'
VENDOR_MODULE = 'jflow.vendors'

BADVALUE = 9999999