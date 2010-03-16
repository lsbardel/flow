from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec

import models as jmodels
from models import InstrumentInterface


def dbmodels():
    '''
    Return a list of Instrument models
    '''
    allmodels = models.get_models(jmodels)
    inst_models = []
    for inst in allmodels:
        ii = inst()
        if isinstance(ii,InstrumentInterface):
            inst_models.append(inst)
    return inst_models

def instrument_ids(astuple = False):
    '''
    Return a list of content types ids
    '''
    allmodels = models.get_models(jmodels)
    ctids = []
    for inst in allmodels:
        ii = inst()
        if isinstance(ii,InstrumentInterface):
            opts = inst._meta
            if not opts.abstract:
                ct = ContentType.objects.get(app_label = opts.app_label,  model = opts.module_name)
                if astuple:
                    ctids.append((ct.pk,ct.name))
                else:
                    ctids.append(ct.pk)
    return ctids

def ctids():
    '''
    Return a queryset of instrument content types ids
    '''
    ids = instrument_ids()
    return ContentType.objects.filter(pk__in = ids)


def cleanmodels():
    imodels = dbmodels()
    for m in imodels:
        objs = m.objects.all()
        for o in objs:
            o.check()


class InstrumentFilterSpec(RelatedFilterSpec):
    '''
    Custom Filter over contenttype representing instrument only
    
    Adapted from django snippets
    http://www.djangosnippets.org/snippets/1051/
    '''
    def __init__(self, f, request, params, model, model_admin):
        super(InstrumentFilterSpec, self).__init__(f, request, 
                                                   params, model, model_admin)
        self.lookup_choices = instrument_ids()
        self.lookup_choices.sort()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': val.upper()}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'instrument_filter', False),
                                   InstrumentFilterSpec))
