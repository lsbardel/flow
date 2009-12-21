from django.contrib import admin

from models import *

class LoggerAdmin(admin.ModelAdmin):
    list_display = ('relevant_date', 'content_type', 'updated')
admin.site.register(Logger,LoggerAdmin)