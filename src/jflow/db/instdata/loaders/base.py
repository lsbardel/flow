import datetime
from decimal import Decimal

from django.conf import settings
from django.db.models import Q

from jflow.db.utils import inv_dict_from_choices
from jflow.utils.decorators import lazyattr
from jflow.db.instdata.models import DataId, Vendor, VendorId, CouponType, BondClass
from jflow.db.instdata.models import BondIssuer, InstrumentCode, equity_type, Exercise_Types
from jflow.db.instdata.utils import instcontent
from jflow.db.geo import countrycode, currency

from master import createsector, getfundtype, tagsfuturecontract, maturityType


equity_type_dict = inv_dict_from_choices(equity_type)
exercise_type_dict = inv_dict_from_choices(Exercise_Types)



def get_loader(source, model, data):
    loader = _loaders.get(source,None)
    if loader:
        return loader(model,data)
    raise ValueError("%s loader not available" % source)
    
    

class loaderMeta(type):
    '''
    PyQuery plugins type class
    '''
    def __new__(cls, name, bases, attrs):
        global _loaders
        super_new = super(loaderMeta, cls).__new__
        new_class = super_new(cls, name, bases, attrs)
        source = new_class.source
        if source:
            if _loaders.has_key(source):
                raise ValueError("%s loader already available" % source)
            _loaders[source] = new_class
        return new_class


class instrumentLoader(object):
    source     = None
    vendorcode = None
    tagseparator = ' '
    __metaclass__ = loaderMeta
    
    def __init__(self, model, data):
        self.idata     = None
        self.sector    = None
        self.group     = None
        self.ddata     = {'default_vendor': self.default_vendor(data)}
        self.result    = 'Not Processed'
        self.model     = str(model)
        self.vendorids = {}
        self.code      = data.pop('code',None)
        if self.vendorcode:
            self.vendorload  = Vendor.objects.get(code = self.vendorcode)
        else:
            self.vendorload  = None
        if self.model:
            self.modelct = instcontent(model)
            self.tags = [self.model]
        else:
            self.tags = []
        self.updatetags(data.get('labels',''))
        if self.model:
            self.instinit(data)
        self.preprocess(data)
        self.save(data)
        
    def default_vendor(self, data):
        code = data.get('default_vendor',None)
        if not code:
            code = settings.DEFAULT_VENDOR_FOR_SITE
        return Vendor.objects.get(code = code)
        
    @lazyattr
    def vendors(self):
        '''
        Dictionary of all available vendors
        '''
        ve = {}
        veds = Vendor.objects.all()
        for v in veds:
            ve[v.code] = v
        return ve
    
    def make_vendorid(self, ticker, v, id):
        '''
        Create a vendorId or update one
        '''
        if ticker and v:
            vid = id.vendorid_set.filter(vendor = v)
            if vid:
                vid = vid[0]
                vid.ticker = ticker
            else:
                vid = VendorId(dataid = id,
                               vendor = v,
                               ticker = ticker)
            vid.save()
            return vid
        else:
            return None
    
    def make_or_update_vendors(self, id, vd):
        '''
        Given a DataId id and a dictionary vd
         key   - vendor code
         value - vendorid ticker or Nothing
        '''
        if id == None:
            return
        self.vendorids = {}
        for v in self.vendors().values():
            ticker = vd.pop(v.code,None)
            vid = self.make_vendorid(ticker,v,id)
            if vid:
                self.vendorids[v.code] = vid
                
    def updatetags(self, tags):
        '''
        update tags checking for repetitions and invalid values
        '''
        alltags = self.tags
        if not isinstance(tags,list):
            tags = str(tags).split(self.tagseparator)
            
        for t in tags:
            if len(t) > 1:
                if t[-1:] == 's':
                    t = t[:-1]
                if len(t) > 1 and t not in alltags:
                    alltags.append(t)
            
    def addifthere(self, key, data = None, val = None):
        if data:
            val = data.pop(keyOrData,None)
            if val:
                self.idata[key] = val
        elif val:
            self.idata[key] = val
            
            
    def futuredata(self, data):
        '''
        Handle future instrument data
        '''
        from jflow.core.finins import date_to_code
        co    = data.get('contract',None)
        if not co:
            raise ValueError("Future contract not available")
        ed    = data.pop('expiry',None)
        if not ed:
            raise ValueError("Future expiry not available")
        name  = '%s %s' % (co.description,ed.strftime("%b %y"))
        self.updatetags(tagsfuturecontract(co))
        mc    = date_to_code(ed)
        self.code  = '%s%s' % (co.code,mc)
        self.ddata.update({'country': co.country,
                           'name': name,
                           'description': name})
        data.pop('security_type',None)
        self.idata = {'contract': co,
                      'first_trade': data.get('first_trade'),
                      'last_trade': data.get('last_trade'),
                      'first_notice': data.get('first_notice'),
                      'first_delivery': data.get('first_delivery'),
                      'last_delivery': data.get('last_delivery')}
    
    def bondclass(self, data):
        '''
        Create a new bond class if not available
        '''
        ccy, country, mult = self.ccy_country_mult(data)
        code = data.pop('bond_class_code',None)
        if not code:
            raise ValueError('"bond_class_code" not specified')
        
        code             = str(code).upper()
        coupon_type      = data.pop('coupon_type',None)
        month_frequency  = int(data.pop('month_frequency'))
        day_count        = data.pop('day_count',None)
        settlement_delay = int(data.pop('settlement_delay',3))
        sovereign        = data.pop('sovereign',False)
        callable         = data.pop('callable',False)
        putable          = data.pop('putable',False)
        convertible      = data.pop('convertible',False)
        description      = data.pop('bond_class_description','')
        maturity         = data.get('maturity_date',None)
        ct               = CouponType.objects.filter(code = coupon_type,
                                                     month_frequency = month_frequency,
                                                     day_count = day_count)
        issuer           = self.get_instrument('issuer',data)
        if not ct:
            raise ValueError('Coupon type not available')
        else:
            ct = ct[0]            
        
        # Get the number of classes for given code
        codeu = '%s_' % code
        #bccc  = BondClass.objects.filter(Q(code = code) | Q(code__startswith=codeu))
        bccc  = BondClass.objects.filter(bondcode = code)
        N = bccc.count()
        bcss  = bccc.filter(sovereign   = sovereign,
                            callable    = callable,
                            putable     = putable,
                            convertible = convertible,
                            coupon_type = ct,
                            curncy      = ccy,
                            country     = country)
        
        if bcss:
            if bcss.count() > 1:
                raise ValueError("Multiple bond classes for %s" % code)
            bc = bcss[0]
            bc.settlement_delay = settlement_delay
            bc.save()
            if issuer:
                bi = BondIssuer.objects.filter(bond_class = bc)
                if bi:
                    bi = bi[0]
                    if bi.data_id != issuer.data_id:
                        raise ValueError("Wrong issuer %s" % issuer) 
        else:
            bondcode = code
            if N:
                code = '%s%s' % (codeu,N+1)
            
            bc = BondClass(code        = code,
                           sovereign   = sovereign,
                           callable    = callable,
                           putable     = putable,
                           convertible = convertible,
                           coupon_type = ct,
                           curncy      = ccy,
                           country     = country,
                           settlement_delay = settlement_delay,
                           description = description,
                           price_type  = 'PRICE',
                           bondcode    = bondcode)
            bc.save()
            if issuer:
                try:
                    issuer = issuer.ic.instrument()
                    bi = BondIssuer(bond_class = bc,
                                    issuer = issuer,
                                    dt = datetime.date.today())
                    bi.save()
                except:
                    pass
        
        self.ddata['country'] = country
        return bc
    
    def ccy_country_mult(self, data):
        '''
        Return a 3-element tuple containing
            currency, country and multiplier
        '''
        ccy  = data.pop('ccy',None)
        mult = data.pop('multiplier',1)
        country = countrycode(data.pop('country',None))
        if not country:
            raise ValueError("Domicile country not defined")
        
        if ccy:
            if ccy == 'GBp':
                mult = 0.01
        if not ccy:
            raise ValueError("Currency not defined")
            
        try:
            ccy = currency(ccy)
        except:
            raise ValueError("Currency not defined")
        return str(ccy), country, mult
        
    def instinit(self, data):
        '''
        Initialise instrument data
        '''
        self.firm_code = data.pop("firm_code","") or ""
        self.sectorgroup(data)
        
        if self.model == "future":
            self.futuredata(data)
        else:
            idata = {}
            self.idata = idata
            if self.model == "bond":
                bc = self.bondclass(data)
                idata['bond_class'] = bc
                c = None
                if bc.coupon_type.code == 'FIXED':
                    c = Decimal(str(data.pop('coupon'))).normalize()
                    idata['coupon'] = c
                self.addifthere('maturity_date', val = self.get_date('maturity_date',data))
                self.addifthere('announce_date', val = self.get_date('announce_date',data))
                self.addifthere('first_settle_date', val = self.get_date('first_settle_date',data))
                self.addifthere('first_coupon_date', val = self.get_date('first_coupon_date',data))
                self.addifthere('accrual_date', val = self.get_date('accrual_date',data))
                idata['collateral_type']   = data.pop('collateral_type',None)
                self.code, name, desc = self.bondcode(c,idata.get('maturity_date',None),bc)
                self.ddata['name'] = name
                self.ddata['description'] = desc
            
            else:
                # FUNDS, EQUITIES, WARRANTS
                #
                self.code = self.make_equity_code(data)
                exch = self.parse_exchange(data.get('exchange',None))
                ccy, country, mult = self.ccy_country_mult(data)
                
                self.ddata['country']     = country
                self.ddata['name']        = data.pop('name','')
                self.ddata['description'] = data.pop('description','')
                
                idata['curncy'] = ccy
                idata['multiplier'] = mult
                idata['settlement_delay'] = int(data.pop('settlement_delay',2))
                if exch:
                    idata['exchange'] = exch
                    
                # FUND
                if self.model == 'fund':
                    ftype = getfundtype(data.get('fund_type',None))
                    if ftype:
                        self.updatetags(ftype.code.lower())
                        idata['type'] = ftype
                    idata['domicile'] = country
                    
                # EQUITY 
                elif self.model == 'equity':
                    idata['security_type'] = data.pop('security_type',1)
                    issuer                 = self.get_instrument('issuer',data)
                    if issuer and issuer.code != self.code:
                        idata['related'] = issuer
                    if self.group:
                        idata['industry_code'] = self.group
                    elif self.sector:
                        idata['industry_code'] = self.sector
                        
                #WARRANT
                elif self.model == "warrant":
                    idata['expiry']        = self.get_date('expiry',data)
                    idata['strike']        = float(data.get('strike',0))
                    idata['underlying']    = self.get_dataid('underlying',data)
                    idata['exercise_type'] = data.get("exercise_type",2)
                
            idata['ISIN'] = data.get('isin','')
            
    def sectorgroup(self, data):
        '''
        Create sector and group
        '''
        sector   = data.pop('sector',None)
        try:
            sectorid = int(data.pop('sectorid',None))
        except:
            sectorid = None
        group    = data.pop('group',None)
        try:
            groupid = int(data.pop('groupid',None))
        except:
            groupid = None
        if sector and sectorid:
            self.sector = createsector(sectorid, sector)
            self.updatetags(self.sector.code)
        if self.sector and group and groupid:
            self.group = createsector(groupid, group, parent = self.sector)
            self.updatetags(self.group.code)
    
    def get_date(self, key, data):
        '''
        parse a date
        '''
        return data.get(key,None)
    
    def get_dataid(self, key, data):
        '''
        parse a dataid object
        '''
        return data.pop(key,None)
    
    def get_instrument(self, key, data):
        id = self.get_dataid(key, data)
        if id:
            try:
                return id.ic.instrument()
            except:
                return None
        else:
            return None
    
    def make_equity_code(self, data):
        return None
    
    def bondcode(self, c, mat, bc):
        '''
        Calculate bond code, name and description
            c     coupon
            mat   maturity
            bc    bond class
        '''
        bcode = bc.bondcode
        if mat:
            smat = '%02d_%s' % (mat.month,str(mat.year)[2:])
            lmat = mat.strftime("%d %b %y")
        else:
            smat = 'PERP'
            lmat = 'PERPETUAL'
            if c:
                smat = '%s_%s' % (c,smat)
                smat.replace('.','_')
        if c:
            lmat = '%s%s %s' % (c,'%',lmat)
        
        code = '%s_%s' % (bcode,smat)
        name = '%s %s' % (bcode,lmat)
        desc = name
        return code,name,desc
        
    def parse_exchange(self, name):
        raise NotImplementedError
    
    def preprocess(self, data):
        pass
    
    def save(self,data):
        '''
        Save data to database
        '''
        code = self.code
        if not code:
            raise ValueError("Could not save. Code missing")
        code = str(self.code)
        id = DataId.objects.filter(code = code)
        if id:
            id = id[0]
        else:
            tags = ' '.join(self.tags)
            id = DataId(code = code, tags = tags, **self.ddata)
            id.save()
        self.id = id
        self.make_or_update_vendors(self.id,data)
        
        if self.model:
            self.saveinstrument()
            
    def saveinstrument(self):
        code = self.id.code 
        try:
            ic = InstrumentCode.objects.get(code = code)
            self.ic = ic
            if self.firm_code and not ic.firm_code:
                ic.firm_code = self.firm_code
                ic.save()
                self.result = 'UPDATED %s' % code
            else:
                self.result = 'UNCHANGED %s' % code
            return
        except:
            # Not there, create the new instrument
            self.ic = InstrumentCode(content_type=self.modelct,
                                     code = code,
                                     firm_code = self.firm_code,
                                     data_id = self.id)
            self.ic.save()
        
        try:
            ct = self.ic.content_type
            iklass = ct.model_class()
            inst   = iklass(id = self.ic.id, **self.idata)
            inst.save()
            self.result = 'ADDED %s' % code
        except Exception, e:
            self.ic.delete()
            self.ic = None
            raise e
            

_loaders = {}

