from django.contrib import admin
from models import *


class CJobAdmin(admin.ModelAdmin):
    list_display = ('name','module','frequency','clock')
admin.site.register(CJob,CJobAdmin)