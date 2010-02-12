from django.contrib import admin
from models import *

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name','url')
admin.site.register(Server,ServerAdmin)
