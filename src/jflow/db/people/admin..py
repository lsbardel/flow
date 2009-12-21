from django.contrib import admin

from models import *

#class PeopleAdmin(admin.ModelAdmin):
#    list_display = ('trader','default_fund','default_history')
#admin.safe_register(PeopleData,PeopleDataAdmin)

class UserPortfolioViewAdmin(admin.ModelAdmin):
    pass
    #list_display = ('user','view','default')
admin.site.register(UserPortfolioView,UserPortfolioViewAdmin)