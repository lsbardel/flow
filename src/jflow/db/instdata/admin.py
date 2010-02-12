from django.contrib import admin

from models import *


#_______________________________________ INLINES
class VendorIdInline(admin.TabularInline):
    model = VendorId

class BondIssuerInline(admin.TabularInline):
    model = BondIssuer

#_______________________________________ ADMINS
class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'summary')
    prepopulated_fields = {'name': ('code',)}

class DataFieldAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'format')

class VendorDataFieldAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'field', 'code')

class VendorIdAdmin(admin.ModelAdmin):
    list_display  = ('ticker', 'vendor', 'dataid',)

class DataIdAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'live', 'get_country', 'tags')
    inlines = [VendorIdInline]
    search_fields = ('code', 'name', 'description', 'tags')

class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('code','name',)

class BondMaturityTypeAdmin(admin.ModelAdmin):
    list_display = ('code','description',)

class CouponTypeAdmin(admin.ModelAdmin):
    list_display = ('code','month_frequency','day_count','description')
    ordering = ('code','month_frequency','day_count')

class FutureContractAdmin(admin.ModelAdmin):
    list_display = ('code','description','type','curncy','country','index','exchange')

class BondClassAdmin(admin.ModelAdmin):
    list_display = ('code','bondcode','description','coupon_type','curncy','country','settlement','issuer','sovereign','callable','putable','convertible')
    search_fields = ('bondcode',)
    list_filter = ('sovereign','callable','putable','convertible','curncy', 'country')
    inlines = [BondIssuerInline]

class BondIssuerAdmin(admin.ModelAdmin):
    list_display = ('bond_class','issuer','ccy','dt')
    search_fields = ('bond_class__code',)

class CollateralTypeAdmin(admin.ModelAdmin):
    list_display = ('name','order')

class FundTypeAdmin(admin.ModelAdmin):
    list_display = ('code','name','openended','description')

class FundManagerAdmin(admin.ModelAdmin):
    list_display = ('code','name','description','website')

class IcAdmin(admin.ModelAdmin):
    list_display = ('code','firm_code','instype','ccy','data_id')
    search_fields = ('code','firm_code')

class BondAdmin(admin.ModelAdmin):
    list_display = ('code','bond_class','ISIN','coupon','maturity_date')
    search_fields = ('ISIN',)

class InstDecompAdmin(admin.ModelAdmin):
    list_display = ('code','instrument','name','composition')

class InstDecompHistoryAdmin(admin.ModelAdmin):
    list_display = ('inst_decomp','dt','composition')

class MktDataAdmin(admin.ModelAdmin):
    list_display = ('vendor_id','field','dt','mkt_value')
    search_fields = ('vendor_id__ticker',)
    ordering      = ('-dt',)

#_______________________________________ REGISTERING
admin.site.register(Vendor,VendorAdmin)
admin.site.register(VendorDataField,VendorDataFieldAdmin)
admin.site.register(VendorId,VendorIdAdmin)
admin.site.register(DataField,DataFieldAdmin)
admin.site.register(DataId,DataIdAdmin)

admin.site.register(Exchange,ExchangeAdmin)
admin.site.register(BondMaturityType,BondMaturityTypeAdmin)
admin.site.register(CouponType,CouponTypeAdmin)
admin.site.register(FutureContract,FutureContractAdmin)
admin.site.register(BondClass,BondClassAdmin)
admin.site.register(BondIssuer,BondIssuerAdmin)
admin.site.register(CollateralType,CollateralTypeAdmin)
admin.site.register(FundManager,FundManagerAdmin)
admin.site.register(FundType,FundTypeAdmin)

admin.site.register(InstrumentCode,IcAdmin)
admin.site.register(Cash3, list_display = ('id','code','curncy','type','extended'))
admin.site.register(FwdCash, list_display = ('id','code','curncy','value_date'))
admin.site.register(Bond,BondAdmin)

admin.site.register(InstDecomp,InstDecompAdmin)
admin.site.register(InstDecompHistory,InstDecompHistoryAdmin)
admin.site.register(MktData,MktDataAdmin)
