from django.conf import settings


DATE_FORMAT = settings.DATE_FORMAT

DEFAULT_VENDOR_FOR_SITE = getattr(settings,
                                 'DEFAULT_VENDOR_FOR_SITE',
                                 'GOOGLE')

DEFAULT_DATA_FIELD = getattr(settings, 'DEFAULT_DATA_FIELD', 'LAST_PRICE')

FIRM_CODE_NAME = getattr(settings,
                         'FIRM_CODE_NAME',
                         'Firm code')

VENDOR_MODULE = getattr(settings,
                       'VENDOR_MODULE',
                       'jflow.vendors')


MAX_RATE_LOADING_THREADS = getattr(settings,
                                   'MAX_RATE_LOADING_THREADS',
                                   3)

LIVE_CALCULATION = getattr(settings,
                           'LIVE_CALCULATION',
                            False)
