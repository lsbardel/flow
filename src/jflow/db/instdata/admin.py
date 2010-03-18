from django.contrib import admin
from django.contrib.admin import helpers
from django import http
from django.template import loader
from django.utils.safestring import mark_safe
from django.contrib.admin.util import unquote
from django.forms.models import modelform_factory
from django.utils import simplejson as json

from models import *
from utils import ctids, dbmodels
from forms import DataIdForm


#_______________________________________ INLINES
class VendorIdInline(admin.TabularInline):
    model = VendorId

class BondIssuerInline(admin.TabularInline):
    model = BondIssuer

#_______________________________________ ADMINS

class DataIdAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'live', 'get_country', 'content_type', 'firm_code', 'tags')
    form          = DataIdForm
    inlines       = [VendorIdInline]
    search_fields = ('code', 'name', 'description', 'tags', 'content_type')
    list_filter   = ('content_type',)
    save_on_top   = True        

    def change_instrument(self, request, obj = None):
        if request.method == 'POST':
            data = request.POST
        else:
            data = request.GET
        data = dict(data.items())
        ctid = int(data.get('content_type',0))
        if ctid:
            ct = ContentType.objects.get(id = ctid)
        else:
            ct = None
        adminForm = self.get_instrument_form(request, ct, obj)
        if adminForm:
            html = loader.render_to_string('admin/instdata/dataid/instrument_form.html',{'adminform':adminForm})
        else:
            html = ''
        data = {'header':'htmls',
                'body': [{'identifier':    '.data-id-instrument',
                          'html':          html}]
                }
        return http.HttpResponse(json.dumps(data), mimetype='application/javascript')
        
    def get_instrument_form(self, request, ct, obj):
        if not ct:
            return ''
        inst = ct.model_class()
        inst_admin = self.admin_site._instruments.get(inst,None)
        if inst_admin:
            mform = inst_admin.get_form(request)
            form = mform()
            return helpers.AdminForm(form, list(inst_admin.get_fieldsets(request)),
                                     inst_admin.prepopulated_fields, inst_admin.get_readonly_fields(request),
                                     model_admin=inst_admin)
        else:
            return None
        
    def add_view(self, request, **kwargs):
        if request.is_ajax():
            return self.change_instrument(request)
        else:
            return super(DataIdAdmin,self).add_view(request, **kwargs)
    
    def change_view(self, request, object_id, **kwargs):
        if request.is_ajax():
            return self.change_instrument(request, self.get_object(request, unquote(object_id)))
        else:
            return super(DataIdAdmin,self).change_view(request, object_id, **kwargs)
        
    def save_form(self, request, form, change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        data = form.cleaned_data
        return form.save(commit=False)
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ctids()
            return db_field.formfield(**kwargs)
        return super(DataIdAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    
class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'summary')
    prepopulated_fields = {'name': ('code',)}

class DataFieldAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'format')

class VendorDataFieldAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'field', 'code')

class VendorIdAdmin(admin.ModelAdmin):
    list_display  = ('ticker', 'vendor', 'dataid',)


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
    list_display = ('code','bondcode','description','curncy','country','issuer','sovereign','convertible')
    search_fields = ('bondcode',)
    list_filter = ('sovereign','convertible','curncy', 'country')
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
    list_display = ('code','dataid','dt','composition')
    ordering      = ('code','-dt')

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
#admin.site.register(CouponType,CouponTypeAdmin)
admin.site.register(FutureContract,FutureContractAdmin)
admin.site.register(BondClass,BondClassAdmin)
admin.site.register(BondIssuer,BondIssuerAdmin)
admin.site.register(CollateralType,CollateralTypeAdmin)
admin.site.register(FundManager,FundManagerAdmin)
admin.site.register(FundType,FundTypeAdmin)

admin.site.register(InstDecomp,InstDecompAdmin)

#admin.site.register(InstrumentCode,IcAdmin)
#admin.site.register(Cash3, list_display = ('id','code','curncy','type','extended'))
#admin.site.register(FwdCash, list_display = ('id','code','curncy','value_date'))
#admin.site.register(MktData,MktDataAdmin)


admin.site._instruments = {}
for inst in dbmodels(): 
    admin.site.register(inst)
    inst_admin = admin.site._registry.pop(inst)
    admin.site._instruments[inst] = inst_admin
    
