from django.contrib import admin

from models import *

class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'summary')
    prepopulated_fields = {'name': ('code',)}
admin.site.register(Vendor,VendorAdmin)

class DataFieldAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'format')
admin.site.register(DataField,DataFieldAdmin)
class VendorDataFieldAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'field', 'code')
admin.site.register(VendorDataField,VendorDataFieldAdmin)

class VendorIdInline(admin.TabularInline):
    model = VendorId

class VendorIdAdmin(admin.ModelAdmin):
    list_display  = ('ticker', 'vendor', 'dataid',)
admin.site.register(VendorId,VendorIdAdmin)

class DataIdAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'live', 'get_country', 'tags')
    inlines = [VendorIdInline]
    search_fields = ('code', 'name', 'description', 'tags')
    #search_fields = ('code','name', 'vendor__name')
admin.site.register(DataId,DataIdAdmin)


class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('code','name',)
admin.site.register(Exchange,ExchangeAdmin)
class BondMaturityTypeAdmin(admin.ModelAdmin):
    list_display = ('code','description',)
admin.site.register(BondMaturityType,BondMaturityTypeAdmin)
class CouponTypeAdmin(admin.ModelAdmin):
    list_display = ('code','month_frequency','day_count','description')
    ordering = ('code','month_frequency','day_count')
admin.site.register(CouponType,CouponTypeAdmin)
class FutureContractAdmin(admin.ModelAdmin):
    list_display = ('code','description','type','curncy','country','index','exchange')
admin.site.register(FutureContract,FutureContractAdmin)
class BondClassAdmin(admin.ModelAdmin):
    list_display = ('code','bondcode','description','coupon_type','curncy','country','settlement','issuer','sovereign','callable','putable','convertible')
    search_fields = ('bondcode','description', 'curncy', 'country')
    list_filter = ('sovereign','callable','putable','convertible','curncy', 'country')
admin.site.register(BondClass,BondClassAdmin)
class BondIssuerAdmin(admin.ModelAdmin):
    list_display = ('bond_class','issuer','dt')
admin.site.register(BondIssuer,BondIssuerAdmin)
class CollateralTypeAdmin(admin.ModelAdmin):
    list_display = ('name','order')
admin.site.register(CollateralType,CollateralTypeAdmin)


class FundTypeAdmin(admin.ModelAdmin):
    list_display = ('code','name','openended','description')
admin.site.register(FundType,FundTypeAdmin)
class FundManagerAdmin(admin.ModelAdmin):
    list_display = ('code','name','description','website')
admin.site.register(FundManager,FundManagerAdmin)

class IcAdmin(admin.ModelAdmin):
    list_display = ('id','code','firm_code','instype','data_id')
    search_fields = ('code',)
admin.site.register(InstrumentCode,IcAdmin)

admin.site.register(Cash3, list_display = ('id','code','curncy','type','extended'))
admin.site.register(FwdCash, list_display = ('id','code','curncy','value_date'))

#class EquityAdmin(admin.ModelAdmin):
#    pass
#admin.safe_register(Equity,EquityAdmin)
#class EtfAdmin(admin.ModelAdmin):
#    exclude = ['benchmark','underlying']
#admin.safe_register(Etf,EtfAdmin)
#class FundAdmin(admin.ModelAdmin):
#    exclude = ['benchmark','underlying']
#admin.safe_register(Fund,FundAdmin)


class InstDecompAdmin(admin.ModelAdmin):
    list_display = ('code','instrument','name','composition')
admin.site.register(InstDecomp,InstDecompAdmin)
class InstDecompHistoryAdmin(admin.ModelAdmin):
    list_display = ('inst_decomp','dt','composition')
admin.site.register(InstDecompHistory,InstDecompHistoryAdmin)

class MktDataAdmin(admin.ModelAdmin):
    list_display = ('vendor_id','field','dt','mkt_value')
    search_fields = ('vendor_id__ticker',)
    ordering      = ('-dt',)
admin.site.register(MktData,MktDataAdmin)

