import csv

from django.core.exceptions import *
from django.contrib.contenttypes.models import ContentType
from django.db import models

#from webspider.gfinance import gfinance

import jflow.db.instdata.models as jmodels
from jflow.db.geo import countryccy, countrycode
from jflow.db.settings import DEFAULT_VENDOR_FOR_SITE

from dataid import dataidhandler
from master import blbexchanges, createsector, getfundtype, tagsfuturecontract


def dbmodels():
    '''
    Return a list of Instrument models
    '''
    allmodels = models.get_models(jmodels)
    inst_models = []
    for inst in allmodels:
        ii = inst()
        if isinstance(ii,jmodels.FincialInstrumentBase):
            inst_models.append(inst)
    return inst_models


def get_instrument_model(model_name):
    if model_name:
        return models.get_model(jmodels.current_app_label, model_name)
    else:
        return None


def adddata(data):
    tags = data.pop('tags',None)
    code = data.pop('code',None)
    if not code:
        raise ValueError, 'Code not available'
    id = jmodels.DataId.objects.filter(code = code)
    if id.count():
        raise ValueError, 'Data Id %s already available' % code
    id = jmodels.DataId(code = code,
                        name = data.pop('name',''),
                        description = data.pop('description',''),
                        country = data.pop('country',None),
                        live = data.pop('live',True),
                        tags = tags)
    id.save()
    return id


def instcontent(model):
    if model == None:
        raise ValueError, 'No Instrument model selected'
    try:
        m = model()
        if isinstance(m,jmodels.FincialInstrumentBase):
            model_name = m._meta.module_name
    except:
        model_name = str(model)
    return ContentType.objects.get(app_label = jmodels.current_app_label,
                                   model = model_name)


def MakeInstrument(ic, model = None, firm_code = None, **kwargs):
    try:
        ct = ic.content_type
        if ct == None and model:
            ct = instcontent(model)
            ic.content_type = ct
            ic.save()
        if firm_code:
            #ic.firm_code = jmodels.numeric_code(firm_code)
            ic.firm_code = firm_code
            ic.save()
        iklass = ct.model_class()
        inst   = iklass(id = ic.id, **kwargs)
        inst.save()
        return ic.instrument()
    except Exception, e:
        ic.delete()
        raise e
    

def Make(model = None,     dataid = None,
         code = None,      user = None,
         firm_code = '',   **kwargs):
    '''
    Create a new financial instrument
    '''
    from django.contrib.admin.models import ADDITION
    IC = jmodels.InstrumentCode
    ct = instcontent(model)
    
    # Check the code
    if dataid:
        code = dataid.code
    
    if code:
        try:
            ic = IC.objects.get(code = code)
        except:
            pass
        else:
            raise ValueError, 'Instrument %s already available' % code
    else:
        raise ValueError, 'Instrument with no code is not possible'
        
    ic = IC(content_type=ct, code = code, firm_code = firm_code, data_id = dataid)
    ic.save()
    return MakeInstrument(ic, **kwargs)


def MakeOrUpdate(id, model = None, user = None,
                 firm_code = '',   **kwargs):
    try:
        ic = jmodels.InstrumentCode.objects.get(code = id.code)
        if fc:
            ic.firm_code = fc
            ic.save()
        return ic,False
    except:
        ic = Make(dataid = id,
                  firm_code = firm_code,
                  model = model,
                  **kwargs)
        return ic,True

def cleanmodels():
    imodels = dbmodels()
    for m in imodels:
        objs = m.objects.all()
        for o in objs:
            o.check()

def clean():
    '''
    Remove redundant instruments
    '''
    ics = jmodels.InstrumentCode.objects.all()
    cl = 0
    for ic in ics:
        inst = ic.instrument()
        if inst == None:
            cl += 1
            ic.delete()
    cleanmodels()



def createshort(data):
    '''
    Create a data ID from minimal information
    '''
    v = data.get('default_vendor',None)
    if v and v.code == 'google':
        ci = gfinance(data['ticker'])
        if ci:
            code = data.get('code',None)
            # if code is provided, remove it from the crawling results
            if code:
                ci.data.pop('code',None)
                
            data.pop('ticker',None)
            data.update(ci.data)
            
            try:
                data['exchange'] = jmodels.Exchange.objects.get(code = data.get('exchange'))
            except:
                data['exchange'] = None
                
            country = data.get('country',None)
            data['curncy'] = countryccy(country)
            
            h  = dataidhandler()
            vs = h.vendors()
            vendors = data.pop('vendors')
            
            if v.code != DEFAULT_VENDOR_FOR_SITE:
                dvs = vs.get(DEFAULT_VENDOR_FOR_SITE)
                if dvs and vendors.has_key(dvs.code):
                    data['default_vendor'] = dvs
            
            vlist   = []
            # Create the vendors tuples
            for k,ticker in vendors.items():
                v = vs.get(k)
                vlist.append((v,ticker))
            data['vendors'] = vlist
            return data
        else:
            raise ValueError, 'Could not find information on the web.'
    else:
        raise NotImplementedError, 'Adding data from %s not implemented' % v



def load(filename):
    idhand = dataidhandler()
    IC  = jmodels.InstrumentCode.objects
    io1 = open(filename,'r')
    res = csv.DictReader(io1)
    for r in res:
        code = r.get('code',None)
        try:
            ic = IC.get(code = code)
        except:
            continue
        fc = r.get('firm_code',None)
        if fc:
            ic.firm_code = fc
            ic.save()
        blb = r.get('blb',None)
        id = ic.data_id
        idhand.make_or_update_vendors(id,r)





def addinstrument(data):
    '''
    Add Instrument from bloomberg
    '''
    idata   = {}
    ddata   = {}
    model   = data.get('model',None)
    ccy     = data.get('ccy',None)
    code    = data.get('code',None)
    mult    = data.get('multiplier',1)
    sett    = data.get('settlement',2)
    isin    = data.get('isin',None)
    exch    = blbexchanges(data.get('exchange',None))
    blb     = data.get('bloomberg',None)
    fc      = data.get('firm_code','')
    tags    = data.get('labels','')
    tags    = tags.split(' ')
    if not blb:
        raise ValueError("Bloomberg ticker not available")
    if isin:
        idata['ISIN'] = isin
    if model:
        model = str(model).lower()
    if ccy:
        if ccy == 'GBp':
            mult = 0.01
        idata['curncy']   = str(ccy).upper()
        idata['multiplier'] = mult
        idata['settlement_delay'] = sett
        idata['exchange'] = exch
    if code is None:
        blbs = blb.split(' ')
        if len(blbs) > 1:
            code = '_'.join(blbs[:-1])
        else:
            code= blb
    ddata['code'] = str(code).upper().replace(' ', '_')
    ddata['country'] = countrycode(data.get('country',None))
    ddata['name'] = data.get('name',None)
    ddata['description'] = data.get('description',None)
    
    if model not in tags:
        tags.append(model)
        
    sector   = data.get('sector',None)
    try:
        sectorid = int(data.get('sectorid',None))
    except:
        sectorid = None
    group    = data.get('group',None)
    try:
        groupid = int(data.get('groupid',None))
    except:
        groupid = None
    sec = None
    grp = None
    if sector and sectorid:
        sec = createsector(sectorid,sector, tags = tags)
    if sec and group and groupid:
        grp = createsector(groupid, group, parent = sec, tags = tags)
    
    if model == 'fund':
        ftype = getfundtype(data.get('fund_type',None),tags)
        if ftype:
            idata['type'] = ftype
        idata['domicile'] = ddata['country'] 
    elif model == 'equity':
        if grp:
            idata['industry_code'] = grp
        elif sec:
            idata['industry_code'] = sec
    
    ddata['tags'] = ' '.join(tags)
    ddata['default_vendor'] = jmodels.Vendor.objects.get(code = 'blb')
    
    idh = dataidhandler()
    id = idh.addorget(ddata)
    idh.make_or_update_vendors(id,{'blb':blb})
    try:
        ic = jmodels.InstrumentCode.objects.get(code = id.code)
        if fc:
            ic.firm_code = fc
            ic.save()
        return 'ALREADY AVAILABLE'
    except:
        Make(dataid = id,
             firm_code = fc,
             model = model,
             **idata)
        return 'ADDED'
    
def addfuture(co, ed, first_trade, last_trade,
              first_notice, first_delivery, last_delivery,
              firm_code, **vendors):
        '''
        Create a future DataId
        '''
        from jflow.core.finins import date_to_code
        name  = '%s %s' % (co.description,ed.strftime("%b %y"))
        tags  = tagsfuturecontract(co)
        mc    = date_to_code(ed)
        code  = '%s%s' % (co.code,mc)
        idh = dataidhandler()
        
        ddata = {'country': co.country,
                 'code': code,
                 'name': name,
                 'description': name,
                 'default_vendor': idh.default_vendor(),
                 'tags': tags}
        idata = {'contract':co,
                 'first_trade': first_trade,
                 'last_trade': last_trade,
                 'first_notice': first_notice,
                 'first_delivery': first_delivery,
                 'last_delivery': last_delivery}
        
        idh = dataidhandler()
        id = idh.addorget(ddata)
        idh.make_or_update_vendors(id,vendors)
        return MakeOrUpdate(id, model = 'future', firm_code = firm_code, **idata)
    