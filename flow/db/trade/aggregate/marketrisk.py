from django.utils.safestring import mark_safe

import math
from basejson import jsonTrade
from logger import log

from jflow.lib import numericts


def calcerror(err):
    return mark_safe(u'<div class="calculation-error">%s</div>' % err)


def numericOrZero(val):
    try:
        return float(val)
    except:
        return 0.0
    
def numericMulOrVal(val,d):
    try:
        return val*d
    except:
        return val
    

def linearSuper(dvals, fvals):
    for k,v in fvals.items():
        d = dvals.get(k,0) + v
        dvals[k] = d
        

        
class allocation(object):
    '''
    Allocation object.
    This object split allocation with respect currencies and subportfolios
    '''
    def __init__(self, name, linear = True):
        self.name   = str(name)
        self.linear = linear
        self.json   = {'name': self.name}
        self.clear()
    
    def __str__(self):
        return self.name
    
    def clear(self):
        self.allocations = []
        self.json['allocations'] = self.allocations 
        self.ccy       = {}     # by currencies
        self.assets    = {}     # by assets
        self.ccyassets = {}     # by currency and assets
        self.allocations.append({'multiple': False,
                                 'data':self.assets})
        self.allocations.append({'multiple': False,
                                 'data':self.ccy})
        self.allocations.append({'multiple': True,
                                 'data':self.ccyassets})

    def add(self, other, assetcode):
        ccys = self.ccy
        aval = self.assets.get(assetcode,0.0)
        
        for c,val in other.ccy.items():
            cval = ccys.get(c,0) + val
            ccys[c] = cval
            aval   += val
            
            ccy_assets = self.ccyassets.get(c,None)
            if ccy_assets is None:
                ccy_assets = {}
                self.ccyassets[c] = ccy_assets
            
            ccy_assets[assetcode] = ccy_assets.get(assetcode,0) + val
        
        self.assets[assetcode] = aval
        
    def normalize(self, navi):
        for k,v in self.ccy.items():
            self.ccy[k] = numericMulOrVal(v,navi)
        for k,v in self.assets.items():
            self.assets[k] = numericMulOrVal(v,navi)
        for av in self.ccyassets.values():
            for k,v in av.items():
                av[k] = numericMulOrVal(v,navi)
            

class MarketRiskBase(jsonTrade):
    '''
    JSON objects which holds market risk information
    '''
    def __init__(self, cache, elem):
        '''
            @param cache:    global cache object
            @param elem:     an instance of positionBase
        '''
        super(MarketRiskBase,self).__init__(cache)
        self.elem                = elem
        self.performance_history = None
        self.allocations         = {}
        self.json_allocations    = []
        self.json['allocations'] = self.json_allocations
        self.addallocation('nav',       'NAV')
        self.addallocation('notional',  'Notional')
        self.addallocation('volc1',     'Volatility C1')
        self.addallocation('avol',      'Aggregate Volatility', linear = False)
        self.clearsimple()
        
    def addallocation(self, code, name, linear = True):
        a = allocation(name, linear = linear)
        self.allocations[code] = a
        self.json_allocations.append(a.json)
        
    def __unicode__(self):
        return '%s of %s' % (self.__class__.__name__,self.elem)
    
    def assetcode(self):
        return self.elem['name']
        
    def clearsimple(self):
        '''
        Initialize scalar quantities
        '''
        self.nav          = 0       # Net Asset Value
        self.notional     = 0       # Notional
        self.absnotional  = 0       # Absolute value of notional exculding cash
        self.stdev        = 0
        self.var          = 0
        self.volc1        = 0       # Volatility with correlation 1
        self.avol         = 0       # Aggregate volatility
        self.mktprice     = ''
        
    def clear(self):
        self.clearsimple()
        for a in self.allocations.values():
            a.clear()
        
    def updateRow(self):
        obj = self.elem
        obj['notional'] = self.notional
        obj['nav']      = self.nav
        obj['mktprice'] = self.mktprice
    
    def rjson(self):
        return self.json
    
    def calculate(self, withRisk = True):
        #self.elem.rjson()
        self._calculate(withRisk = withRisk)
        self.json['nav']      = self.nav
        self.json['notional'] = self.notional
        self.json['stdev']    = self.stdev
        self.json['var']      = self.var
        self.json['mktprice'] = self.mktprice
        
        # POST CALCULATION
        self.postcalc(withRisk)
        
        # once calculation is finished we updates the table rows
        self.updateRow()
        return self
    
    def postcalc(self,withRisk):
        pass
    
    def _calculate(self, withRisk = True):
        pass
    
    def calculateRelativeValues(self, mrbase = None, withRisk = True):
        '''
        Calculate values with respect root Node
        '''
        try:
            elem = self.elem
            navi = 1./mrbase.nav
            navalloc = numericMulOrVal(self.nav,navi)
            notalloc = numericMulOrVal(self.notional,navi)
            volc1    = numericMulOrVal(self.volc1,navi)
            avol     = numericMulOrVal(self.avol,navi)
            lev1     = numericMulOrVal(self.absnotional,navi)
            self.json['navallocation'] = navalloc
            self.json['notallocation'] = notalloc
            elem['navallocation'] = navalloc
            elem['notallocation'] = notalloc
            elem['volc1']         = volc1
            elem['vol']           = avol
            elem['lev1']          = lev1
            
            if withRisk:
                for a in self.allocations.values():
                    a.normalize(navi)
        except:
            pass
    



class MarketRiskPosition(MarketRiskBase):
    '''
    JSON Risk object for a single position
    
    @param cache: cache object
    @param elem: instance of portfoliotree.jsonPortfolio with
                 elem.isposition set
    '''
    def __init__(self, cache, elem):
        self.decomposition = None
        super(MarketRiskPosition,self).__init__(cache, elem)
        
    def _calculate(self, withRisk = True):
        elem  = self.elem
        pos   = elem.isposition
        # finins instance
        fin   = pos.fininst
        tinst = fin.type
        mr    = pos.mktrisk
        fx    = elem._fxcross or 1.0
        
        # Set the absolute value of notional for leverage calculation
        if fin.iscash:
            mr.absnotional = 0
        else:
            try:
                mr.absnotional = math.fabs(mr.notional)
            except:
                pass
        
        try:
            self.nav         = mr.nav*fx
            self.notional    = mr.notional*fx
            self.absnotional = mr.absnotional*fx
        except Exception, e:
            elem.update()
            self.err(e, msg = 'Failed market risk multiplication.')
            
        self.mktprice = mr.mktprice
        
        # Quick and dirty calculation of historical notional
        if not self.performance_history:
            self.calculate_history()
        
        # Calculate the volatility
        if self.performance_history and self.notional:
            try:
                delta = self.performance_history.econometric.slogdelta()
                self.volc1 = self.notional*delta.econometric.vol()
            except Exception, e:
                self.performance_history = None
                self.err(e,
                         msg = 'Failed market volatility calculation.',
                         sendmail = False)
                self.volc1 = calcerror(e)
        else:
            self.volc1 = calcerror('Missing historical information')
        self.avol = self.volc1
            
        if withRisk:
            for k,alloc in self.allocations.items():
                self.splitalloc(k,alloc)
    
    
    def splitalloc(self, code, alloc):
        '''
        Split allocation.
        If underlying has a decomposition, split accordingly
        otherwise just assign the currency
        '''
        elem      = self.elem
        pos       = elem.isposition
        idb       = pos.fininst.dbinstrument
        if self.decomposition is None:
            self.decomposition = idb.lineardecomp()
        
        v = numericOrZero(getattr(self,code))
        ccys   = alloc.ccy
        assets = alloc.assets
        if self.decomposition.valid:
            td = self.decomposition.delta
            if code == 'notional':
                setattr(self,code,td*v)
                for d in self.decomposition:
                    ccy = str(d.ccy) 
                    de  = d.delta
                    cval = ccys.get(ccy,0.0) + de*v
                    ccys[ccy] = cval
            else:
                for d in self.decomposition:
                    ccy = str(d.ccy) 
                    de  = d.delta/td
                    cval = ccys.get(ccy,0.0) + de*v
                    ccys[ccy] = cval
        else:
            ccys[pos.ccy] = v
            
        assets[self.assetcode()] = v
    
    
    def calculate_history(self):
        '''
        Calculate historical notional for position
        '''
        elem = self.elem
        pos  = elem.isposition
        fin  = pos.fininst
        pts  = fin.histories.get('price',None)
        if pts and pts.ts:
            tc = numericts()
            for k,v in pts.ts.items():
                fin.mktprice = v
                tc[k] = fin.notional(pos.size)
            if elem._fxhistory:
                tc = tc*elem._fxhistory
            fin.mktprice = self.mktprice
            self.performance_history = tc;






class MarketRiskPortfolio(MarketRiskBase):
    '''
    Specialization of marketrisk for a portfolio
    '''
    def __init__(self, cache, elem):
        super(MarketRiskPortfolio,self).__init__(cache, elem)
        
    def _calculate(self, withRisk = True):
        self.clear()
        elem = self.elem
        #TODO
        #maybe we can just loop over elem.element_objects.values
        #that would save a key search on the dictionary 
        for child in elem.children:
            el = elem.element_objects.get(child)
            self.add(el.mktrisk, withRisk = withRisk)
        
        if self.performance_history:
            ph = self.performance_history.pop(0)
            for h in self.performance_history:
                ph += h
            self.performance_history = ph
            if self.notional:
                try:
                    delta = ph.econometric.slogdelta()
                    self.avol = self.notional*delta.econometric.vol()
                except Exception, e:
                    self.avol = calcerror(e)
    
    def assetcode(self):
        return self.elem.code
    
    def postcalc(self, withRisk):
        elem = self.elem
        if elem.parent == None:
            self.calculateRelativeValues(withRisk = withRisk)
            
    def calculateRelativeValues(self, mrbase = None, withRisk = True):
        '''
        Calculate values with respect root Node
        '''
        if mrbase == None:
            mrbase = self
        super(MarketRiskPortfolio,self).calculateRelativeValues(mrbase, withRisk = withRisk)
        elem = self.elem
        for child in elem.children:
            el = elem.element_objects.get(child)
            el.mktrisk.calculateRelativeValues(mrbase, withRisk = withRisk)
        
    
    def add(self, other, withRisk = False):
        try:
            self.nav         += numericOrZero(other.nav)
            self.notional    += numericOrZero(other.notional)
            self.absnotional += numericOrZero(other.absnotional)
            self.volc1       += numericOrZero(other.volc1)
            
            if other.performance_history:
                if not self.performance_history:
                    self.performance_history = [other.performance_history]
                else:
                    self.performance_history.append(other.performance_history)
                    
            # Add element to allocation risk
            if withRisk:
                for k,alloc in self.allocations.items():
                    other_alloc = other.allocations.get(k)
                    if alloc.linear:
                        alloc.add(other_alloc, other.assetcode())
                    else:
                        alloc.assets[other.assetcode()] = getattr(other,k)
                        
        except Exception, e:
            self.update()
            self.err(e,'Failed market risk addition width %s' % other)
    
    
    def add_alloc(self, code, alloc, other):
        alloc
        
        
            
            

