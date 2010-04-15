import os
from jflow.utils.importlib import import_module
from jflow.conf import global_settings


ENVIRONMENT_VARIABLE = "JFLOW_SETTINGS_MODULE"


class Settings(object):
    
    def __init__(self, settings_module):
        self.settings_module = settings_module
        
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting == setting.upper():
                setattr(self, setting, getattr(global_settings, setting))
        
        if settings_module:
            for setting in dir(settings_module):
                if setting == setting.upper():
                    setattr(self, setting, getattr(settings_module, setting))
        


def get_settings():
    settings_module = os.environ.get(ENVIRONMENT_VARIABLE,None)
    
    if settings_module: 
        try:
            mod = import_module(settings_module)
        except ImportError, e:
            raise ImportError("Could not import settings '%s': %s" % (settings_module, e))
    else:
        mod = None
    
    return Settings(mod)


settings = get_settings()
