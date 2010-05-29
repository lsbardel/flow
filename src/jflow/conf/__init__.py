import os
from jflow.utils.importlib import import_module
from jflow.conf import global_settings


#If django is installed used the django setting object
try:
    from django.conf import settings as django_settings
except:
    django_settings = None 


ENVIRONMENT_VARIABLE = "JFLOW_SETTINGS_MODULE"


class Settings(object):
    pass

def fill(self, settings_module):
        
    # update this dict from global settings (but only for ALL_CAPS settings)
    for setting in dir(global_settings):
        if setting == setting.upper():
            if not hasattr(self,setting):
                setattr(self, setting, getattr(global_settings, setting))
        
    return self    


def get_settings():
    settings_module = os.environ.get(ENVIRONMENT_VARIABLE,None)
    
    if settings_module: 
        try:
            mod = import_module(settings_module)
        except ImportError, e:
            raise ImportError("Could not import settings '%s': %s" % (settings_module, e))
    else:
        mod = None
    
    sett = django_settings
    if not sett:
        sett = Settings()
    
    return fill(sett,mod)


settings = get_settings()
