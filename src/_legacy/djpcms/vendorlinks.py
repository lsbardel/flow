from django.utils.text import capfirst
from django.db import models
from django.conf import settings

from djpcms.html import table, link
from djpcms.views.base import modelurl

from jflow.db.instdata.models import Vendor

def vendorlinks(obj):
    '''
    Return a two columns table of vendors links
    obj must be a DataId instance
    '''
    vid = obj.vendorid_set.all()
    if vid.count():
        body = table(cn='plain')
        for v in vid:
            vendor = v.vendor
            vi = vendor.interface()
            tk = v.ticker
            if vi:
                url = vi.weblink(tk)
                if url:
                    tk = link(url = url, inner = tk, target = '_blank')
            body.addrow(str(vendor), tk)
        return body
    return None


def additionalidinfo(obj,request):
    tb = table(cn='plain')
    dv = obj.default_vendor
    if dv == None:
        dv = Vendor.objects.get(code = settings.DEFAULT_VENDOR_FOR_SITE)
        obj.default_vendor = dv
        obj.save()
    tb.addrow('Default Vendor',str(obj.default_vendor))
    ic = obj.ic
    if ic:
        info = ic.infodict()
        info.pop('code')
        info.pop('tags')
        info.pop('description')
        for k,v in info.items():
            c = capfirst(k.replace('_',' '))
            tb.addrow(c,v)
        idx = ic.get_underlying()
        if idx:
            url = modelurl(idx,request,'view')
            if url:
                tb.addrow('Underlying',link(url = url, inner = idx.code))
    return tb


def decomposition(obj, request):
    ic = obj.ic
    if ic:
        inst = ic.instrument()
        deco = inst.lineardecomp()
        if not deco:
            return
        tb = table(cn='plain', cols = 4)
        tb.addheader('beta','currency','underlying','underlying currency')
        for d in deco:
            u  = d.underlying
            b  = '%s%s' % (int(10000*d.delta)/100,'%')
            c  = u
            uc = d.undccy
            if isinstance(u,models.Model):
                url = modelurl(u,request,'view')
                if url:
                    c = link(url = url, inner = u.code)
            else:
                uc = 'Index not in database'
                    
            tb.addrow(b,d.ccy,c,uc)
        return tb
    else:
        return
    