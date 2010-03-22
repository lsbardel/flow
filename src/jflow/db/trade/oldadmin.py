from django.contrib import admin

from models import *



class FundHolderAdmin(admin.ModelAdmin):
    list_display = ('code','description','fund_manager')
admin.site.register(FundHolder,FundHolderAdmin)

class TraderAdmin(admin.ModelAdmin):
    list_display = ('user','fullname','is_active','is_staff','is_superuser','fund_holder','default_fund','default_history','machine','port','server_active')
    list_filter  = ('fund_holder',)
admin.site.register(Trader,TraderAdmin)

class FundAdmin(admin.ModelAdmin):
    list_display = ('code','firm_code', 'description','curncy','fund_holder','parent','dataid')
    list_filter  = ('fund_holder',)
admin.site.register(Fund,FundAdmin)

class CustodyAccountAdmin(admin.ModelAdmin):
    list_display = ('code','name','fund','dummy')
    list_filter  = ('fund',)
admin.site.register(CustodyAccount,CustodyAccountAdmin)

class PositionAdmin(admin.ModelAdmin):
    list_display = ('instrumentCode','fund','status','open_date','close_date','custodian')
    list_filter  = ('status','fund',)
    ordering = ('-open_date',)
    search_fields = ('instrumentCode__code',)
admin.site.register(Position,PositionAdmin)

class PortfolioViewAdmin(admin.ModelAdmin):
    list_display = ('name','fund','default','user','description')
admin.site.register(PortfolioView,PortfolioViewAdmin)

class UserViewDefaultAdmin(admin.ModelAdmin):
    list_display = ('user','view')
admin.site.register(UserViewDefault,UserViewDefaultAdmin)

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('code','view','fund','parent','cash_account')
admin.site.register(Portfolio,PortfolioAdmin)

class PositionHistoryAdmin(admin.ModelAdmin):
    #date_hierarchy = 'dt'
    ordering = ('-dt',)
    #list_filter   = ('dt',)
    list_display = ('position','dt','size','value','dirty_value')
    search_fields = ('position',)
admin.site.register(PositionHistory,PositionHistoryAdmin)

class PortfolioDisplayComponentInline(admin.TabularInline):
    model = PortfolioDisplayComponent
    extra = 5

class PortfolioDisplayAdmin(admin.ModelAdmin):
    list_display = ('code','name','description','display')
    inlines = [PortfolioDisplayComponentInline]
admin.site.register(PortfolioDisplay,PortfolioDisplayAdmin)

class PortfolioDisplayElementAdmin(admin.ModelAdmin):
    list_display = ('code','name','description','formatter','sortable','dynamic','order')
admin.site.register(PortfolioDisplayElement,PortfolioDisplayElementAdmin)

class ManualTradeAdmin(admin.ModelAdmin):
    list_display = ('user','open_date','close_date','portfolio','quantity','price','position')
admin.site.register(ManualTrade,ManualTradeAdmin)

