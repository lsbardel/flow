from django.conf import settings


DATE_FORMAT = settings.DATE_FORMAT

DEFAULT_VENDOR_FOR_SITE = getattr(settings,
                                 'DEFAULT_VENDOR_FOR_SITE',
                                 'google')

LOWER_CASE_VENDORS = getattr(settings,
                             'LOWER_CASE_VENDORS',
                             True)

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
