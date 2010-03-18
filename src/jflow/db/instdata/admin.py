from django.contrib import admin
from django.contrib.admin import helpers
from django import http
from django.template import loader
from django.utils.safestring import mark_safe
from django.forms.models import modelform_factory
from django.utils import simplejson as json

from models import *
from utils import ctids, dbmodels
from forms import DataIdForm


#_______________________________________ INLINES
class VendorIdInline(admin.TabularInline):
    model = VendorId

class InstrumentInline(admin.StackedInline):
    template = 'admin/instdata/dataid/edit_inline/stacked.html'
    
class EquityInline(InstrumentInline):
    model = Equity
class BondInline(InstrumentInline):
    model = Bond

class BondIssuerInline(admin.TabularInline):
    model = BondIssuer

#_______________________________________ ADMINS

class DataIdAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'live', 'get_country', 'content_type', 'firm_code', 'tags')
    form          = DataIdForm
    inlines       = [VendorIdInline]
    instruments   = [EquityInline,BondInline]
    search_fields = ('code', 'name', 'description', 'tags', 'content_type')
    list_filter   = ('content_type',)
    save_on_top   = True
    
    def __init__(self, model, admin_site):
        self.inline_models = [inline.model for inline in self.inlines]
        self.inlines += self.instruments
        super(DataIdAdmin,self).__init__(model, admin_site)            

    def change_instrument(self, request, obj = None):
        if request.method == 'POST':
            data = request.POST
        else:
            data = request.GET
        data = dict(data.items())
        ctid = int(data.get('content_type',0))
        inst = None
        html = ''
        if ctid:
            try:
                ct = ContentType.objects.get(id = ctid)
                inst = ct.model_class()
                inst_admin = self.admin_site._instruments.get(inst,None)
                if inst_admin:
                    mform = inst_admin.get_form(request)
                    form = mform()
                    adminForm = helpers.AdminForm(form, list(inst_admin.get_fieldsets(request)),
                                                  inst_admin.prepopulated_fields, inst_admin.get_readonly_fields(request),
                                                  model_admin=inst_admin)
                    html = loader.render_to_string('admin/instdata/dataid/instrument_form.html',{'adminform':adminForm})
            except Exception, e:
                pass
        
        data = {'header':'htmls',
                'body': [{'identifier':    '.data-id-instrument',
                          'html':          html}]
                }
        return http.HttpResponse(json.dumps(data), mimetype='application/javascript')
        
    def add_view(self, request, **kwargs):
        if request.is_ajax():
            return self.change_instrument(request)
        else:
            return super(DataIdAdmin,self).add_view(request, **kwargs)
            
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        inlines = context.pop('inline_admin_formsets')
        new_inlines = []
        instruments = []
        for inline in inlines:
            #new_inlines.append(inline)
            isin = False
            for model in self.inline_models:
                if inline.opts.model == model:
                    new_inlines.append(inline)
                    isin = True
                    break
            if not isin:
                instruments.append(inline)                    
        context.update({'inline_admin_formsets': new_inlines,
                        'instruments': instruments})
        return super(DataIdAdmin,self).render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)
        
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
    
