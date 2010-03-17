from geo import currencydb
from instdata.models import DataId, VendorId, Vendor


def addvendor(v,id,t):
    vid = VendorId.objects.filter(vendor = v, dataid = id)
    if vid:
        return vid[0]
    else:
        vid = VendorId(ticker = t, dataid = id, vendor = v)
        vid.save()
        return vid


def ccy2dataid(default_vendor = 'blb'):
    dv   = Vendor.objects.get(code = default_vendor)
    blb  = Vendor.objects.get(code = 'blb')
    ecb  = Vendor.objects.get(code = 'ecb')
    ccys = currencydb()
    for ccy in ccys.values():
        if ccy.code == 'USD':
            continue
        try:
            id = DataId.objects.get(code = ccy.code)
            id.tags = 'currency spot forex index'
            id.save()
        except:
            id = DataId(code = ccy.code,
                        name = ccy.description(),
                        default_vendor = dv,
                        country = ccy.default_country)
            id.save()
        
        addvendor(blb,id,'%s Curncy' % ccy.code)
        addvendor(ecb,id,ccy.code)