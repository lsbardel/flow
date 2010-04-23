from django.conf import settings
if getattr(settings,'OLD_JFLOW_SCHEMA',False):
    from _models import *
else:
    from newmodels import *
