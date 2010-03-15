from django.db import models
from django.contrib.contenttypes.models import ContentType

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

def ctids():
    '''
    Return a list of content types ids
    '''
    allmodels = models.get_models(jmodels)
    inst_models = []
    for inst in allmodels:
        ii = inst()
        if isinstance(ii,InstrumentInterface):
            opts = inst._meta
            if not opts.abstract:
                ct = ContentType.objects.get(app_label = opts.app_label,  model = opts.module_name)
                inst_models.append(ct.pk)
    return ContentType.objects.filter(pk__in = inst_models)


def cleanmodels():
    imodels = dbmodels()
    for m in imodels:
        objs = m.objects.all()
        for o in objs:
            o.check()


def instcontent(model):
    if model == None:
        raise ValueError, 'No Instrument model selected'
    try:
        m = model()
        if isinstance(m,InstrumentInterface):
            model_name = m._meta.module_name
    except:
        model_name = str(model)
    return ContentType.objects.get(app_label = current_app_label,
                                   model = model_name)