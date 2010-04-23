from django.conf import settings
if getattr(settings,'OLD_JFLOW_SCHEMA',False):
    from oldadmin import *
else:
    from newadmin import *