'''
Rollback positions and positions history to a specified date
'''
import logging
import optparse
import os
import datetime
import dateutil.parser
 
from django.contrib.auth.models import User
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
from django.utils.dateformat import format

from jflow.db.trade.forms import get_trader
 
_special_tags = {}
 
class Command(BaseCommand):
    help = "Check trade database for anomalies"
 
    def handle(self, *args, **options):
        for user in User.objects.all():
            get_trader(user)