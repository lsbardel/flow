#!/usr/bin/env python
from django.core.management import execute_manager
try:
    import settings
except:
    import global_settings as settings

if __name__ == "__main__":
    execute_manager(settings)
