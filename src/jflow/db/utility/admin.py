from djpcms import adminsite as admin
from models import *

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name','url')
admin.safe_register(Server,ServerAdmin)
