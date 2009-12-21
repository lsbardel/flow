from django.db import models
from django.contrib.contenttypes.models import ContentType

import models as jmodels
from models import FincialInstrumentBase, current_app_label

def dbmodels():
    '''
    Return a list of Instrument models
    '''
    allmodels = models.get_models(jmodels)
    inst_models = []
    for inst in allmodels:
        ii = inst()
        if isinstance(ii,FincialInstrumentBase):
            inst_models.append(inst)
    return inst_models


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
        if isinstance(m,FincialInstrumentBase):
            model_name = m._meta.module_name
    except:
        model_name = str(model)
    return ContentType.objects.get(app_label = current_app_label,
                                   model = model_name)