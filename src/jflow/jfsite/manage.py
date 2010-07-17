#!/usr/bin/env python
import sys
import os

from django.core.management import execute_manager

try:
    import settings
except:
    import global_settings as settings


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            os.environ['JFLOW_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.tests'
            os.environ['STDNET_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.tests'
    execute_manager(settings)
