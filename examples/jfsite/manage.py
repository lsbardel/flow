#!/usr/bin/env python
import sys
import os
import environment
import jflow
from django.core.management import execute_manager

if __name__ == "__main__":
    jflow.set_settings('jfsite.allsettings.debug')
    execute_manager()
