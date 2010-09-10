import csv

from jflow.db.instdata.models import InstrumentCode, Vendor

class dumpcsv(object):
    
    def __init__(self,
                 write_header = True,
                 file_name = 'T:\Data\Internal Data\QMData\prospero_data.csv'):
        io1 = open(file_name,'w')
        fields    = self.fields()
        self.res  = csv.DictWriter(io1,fields)
        self.rows = []
        if write_header and fields:
            headernames = dict(zip(fields,fields))
            self.rows.append(headernames)
        self.write()
    
    def fields(self):
        return {}
    
    def write(self):
        pass
    
    
class dumpinst(dumpcsv):
    
    def __init__(self, with_firm_code = True, **kwargs):
        self.with_firm_code = with_firm_code
        vends = {}
        vends['blb']    = Vendor.objects.get(code = 'blb')
        vends['google'] = Vendor.objects.get(code = 'google')
        vends['yahoo']  = Vendor.objects.get(code = 'yahoo')
        self.vends = vends
        super(dumpinst,self).__init__(**kwargs)
        
    def fields(self):
        return ['code',
                'blb',
                'firm_code',
                'name',
                'google',
                'yahoo']
        
    def empty_string_or_code(self, vids, code):
        v = self.vends[code]
        vid = vids.filter(vendor = v)
        if vid:
            return vid[0].ticker
        else:
            return ''
        
    def write(self):
        ics = InstrumentCode.objects.all()
        fields = self.fields()
        rows = []
        for ic in ics:
            inst = ic.instrument()
            if inst == None:
                ic.delete()
                continue
            if not inst.has_firm_code() and self.with_firm_code:
                continue
            id   = ic.data_id
            if id:
                vids = id.vendorid_set
                val = [ic.code,
                       self.empty_string_or_code(vids,'blb'),
                       ic.firm_code,
                       id.name,
                       self.empty_string_or_code(vids,'google'),
                       self.empty_string_or_code(vids,'yahoo')]
                vr = dict(zip(fields,val))
                self.rows.append(vr)
        self.res.writerows(self.rows)