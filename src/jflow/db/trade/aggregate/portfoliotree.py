'''
JSON classes used in the protfolio tree view.

This classes are used only when we need the tree
structure provided by subportfolios
'''

from jflow.db.trade.models import Position, PortfolioView, Fund, Portfolio
from jflow.db.trade.utils import get_object_id, get_object_from_id
from jflow.rates import get_history, get_rate
from jflow.utils.observer import lazyobject
from jflow.core.dates import get_livedate
from jflow.core.rates import objects as rateObjects

from logger import log
from basejson import extract, listpop, positionBase
from marketrisk import MarketRiskPosition, MarketRiskPortfolio
from position import jsonPosition, jsonFund
from position import MktPositionInterface, POSITION_STATUS

        
    

class jsonPortfolio(positionBase, MktPositionInterface):
    '''
    A Portfolio View JSON object
    This class is used in the json Portfolio Tree.
    It maintain a node in the portfolio view. This node can be a
    position, a subportfolio or a fund.
    '''
    def __init__(self, tree, obj, parent = None):
        cache            = tree.cache
        self.isposition  = False
        if isinstance(obj,jsonFund):
            obj = obj.dbobj
            
        if isinstance(obj,jsonPosition):            
            self.isposition   = obj
            obj               = obj.dbobj
            self.folder       = False
            self.movable      = True
            self.__mkt_risk   = MarketRiskPosition(cache,self)
            self.fund         = parent.fund
        elif isinstance(obj,Fund):
            self.isfund       = True
            self.__mkt_risk   = MarketRiskPortfolio(cache,self)
            self.fund         = obj
        else:
            self.canaddto     = True
            self.editable     = True
            self.movable      = True
            self.__mkt_risk   = MarketRiskPortfolio(cache,self)
            self.fund         = parent.fund
                        
        self.tree            = tree
        self.parent          = parent
        self.children        = []
        positionBase.__init__(self, cache, obj, tree.dte)
        
    
    def __get_mktrisk(self):
        '''
        refresh if needed and return the market risk object
        '''
        self.refresh()
        return self.__mkt_risk
    mktrisk = property(fget = __get_mktrisk)
    
    def build(self, **kwargs):
        parent = self.parent
        self._build()
        self.register()
        self.setparent(parent)
        
    def register(self):
        '''
        Override registration
        '''
        reg = False
        if self.isposition:
            self.isposition.register()
            if not self.rowdata:
                self.rowdata = self.isposition.rowdata[:]
                self.setstaticjson()
                self.register_to_fxcross(self.cache)
                reg = True
        else:
            reg = positionBase.register(self)
        if reg:
            json              = self.json
            json['folder']    = self.folder
            json['canaddto']  = self.canaddto
            json['editable']  = self.editable
            json['movable']   = self.movable
            json['tree']      = self.children
        return reg
        
    def __get_instype(self):
        if self.isfund:
            return 'portfolio'
        elif self.isposition:
            return 'position'
        else:
            return 'folder'
    instype = property(fget = __get_instype)
        
    def __get_view(self):
        return self.tree.view
    view = property(fget = __get_view)
    
    def __get_elements(self):
        return self.tree.elements
    elements = property(fget = __get_elements)
    
    def __get_element_objects(self):
        return self.tree.element_objects
    element_objects = property(fget = __get_element_objects)
        
    def setparent(self, parent):
        if self.parent:
            self.parent.removechild(self)
        pid = None
        self.parent = parent
        if parent:
            pid = parent.id
            self.json['parent']  = pid
            parent.children.append(self.id)
            if self.isfund:
                self.fund = self.dbobj
            else:
                self.fund = self.parent.fund
            #
            # Set the parent as an observer
            self.attach(parent)
            
            
    def removechild(self, el):
        el.detach(self)
        return listpop(self.children, el.id)
        
    def __unicode__(self):
        return '%s in %s' % (self.dbobj,self.view)
    
    def __get_ccy(self):
        return self.isposition.ccy
    ccy = property(fget = __get_ccy)
    
    def _build(self):
        dte          = self.dte
        obj          = self.dbobj
        folders      = []
        parent       = self.parent
        ppositions   = None
        self.parent  = None
        
        # Fund
        if self.isfund:
            jsonfund     = self.cache.portfolio(obj, dte)
            folders      = jsonfund.funds
            if not folders:
                self.canaddto    = True
                folders          = obj.rootfolders(self.view)
                self.positionset = jsonfund.positionsdict()
                
        # Position
        elif self.isposition:
            self.isposition.attach(self)
            
        # Portfolio
        else:
            folders          = obj.subfolders()
            self.positionset = parent.positionset 
            ppositions       = obj.position_for_date(dte.dateonly, status = POSITION_STATUS)
                
        
        elements  = self.elements
        elemobjs  = self.element_objects
        
        # Add self to the elements dictionaries    
        elements[self.id] = self.json
        elemobjs[self.id] = self
        
        # Loop over folders and create new jsonPortfolios
        for f in folders:
            self.append(f)
        
        # Now handle positions for funds    
        if self.isfund and self.positionset:
            for jp in self.positionset.values():
                jf = self.append(jp)
                self.positionset.pop(jf.id)
        elif ppositions:
            for p in ppositions:
                id = get_object_id(p)
                jp = self.positionset.pop(id,None)
                if jp:
                    jf = self.append(jp)
                else:
                    log("Critical Warning, position %s not in portfolio" % p)
            
            
    def append(self, f):
        '''
        1 - Create a new jsonPortfolio element from f
        2 - Register self as observer of the new jsonPortfolio element
        
        @param f: portfolio element 
        @return the new jsonPortfolio element
        '''
        jf = jsonPortfolio(self.tree, f, self)
        jf.build()
        return jf
    
    def name(self):
        n = getattr(self.dbobj,"name",None)
        if n:
            if callable(n):
                n = n()
            return n
        return ""
            
    def refresh_me(self):
        positionBase.refresh_me(self)
        self.__mkt_risk.calculate(withRisk = True)

    def calc_ccy(self):
        return self.fund.curncy
        


class jsonPortfolioTree(positionBase):
    '''
    A Portfolio Tree JSON object
    '''
    def __init__(self, cache, view, dte):
        super(jsonPortfolioTree,self).__init__(cache, view, dte)
        self.elements         = {}
        self.element_objects  = {}
        self.json['elements'] = self.elements
        
    def _build(self):
        dt     = self.dte.dateonly
        pf = self.cache.portfolio(self.fund,dt)
        pf.addcallback(self.register)
        
    def register(self, p):
        self.root = jsonPortfolio(self, self.fund)
        # attach self to the jsonPortfolio root
        # IMPORTANT
        self.root.attach(self)
        self.root.build()
        self.json['root'] = self.root.id
        self._closebuild()
        
    def __unicode__(self):
        return u'%s' % self.view
    
    def __get_fund(self):
        return self.dbobj.fund
    fund = property(fget = __get_fund)
    
    def __get_view(self):
        return self.dbobj
    view = property(fget = __get_view)
    
    def get(self, id):
        return self.element_objects.get(id,None)
    
    def pop(self, id):
        '''
        Remove a node from portfolio tree
        '''
        el = self.element_objects.get(id,None)
        if el and el.editable:
            self.element_objects.pop(id,None)
            self.elements.pop(id,None)
            p = el.parent
            if p:
                listpop(p.children, id)
            
            children = el.children[:]
            for cid in children:
                c = self.element_objects.get(cid,None)
                c.parent = None
                if not c:
                    continue
                c.setparent(p)
                
                # And now the database stuff
                if isinstance(c.dbobj,Portfolio):
                    c.dbobj.setparent(p.dbobj)
                elif isinstance(p.dbobj,Portfolio):
                    p.dbobj.position.add(c.dbobj)
                    
            if not p.isfund:
                p.dbobj.save()
                
            el.dbobj.delete()
            
            self.view.save()
        else:
            el = None
        return el
    
    def marketRisk(self, id):
        node = self.element_objects.get(id,None)
        if node:
            log.msg("Calculating market risk for %s" % node)
            self.refresh()
            return node.mktrisk
        else:
            return None
        
    
    def addfolder(self, code, parent_id):
        parent = self.element_objects.get(parent_id,None)
        if parent:
            pobj = parent.dbobj
            p      = self.view.addFolder(pobj, code)
            if p:
                pjson = parent.append(p)
                self.view.save()
                return pjson
            else:
                return None
            
    def editfolder(self, data):
        id = data.get('id',None)
        if id:
            node = self.element_objects.get(id,None)
            if node:
                p = node.dbobj
                if isinstance(p,Portfolio):
                    code = data.get('code',None)
                    name = data.get('name',None)
                    desc = data.get('description',None)
                    p.setcode(code)
                    node.setcode(p.code)
                    if name is not None:
                        p.name = name
                    if desc is not None:
                        p.description = desc
                    p.save()
                    node.reregister()
                    return node
        return None
                
            
    def move(self, id, target):
        el = self.element_objects.get(id,None)
        tg = self.element_objects.get(target,None)
        if el and tg and el.movable and tg.canaddto and el != tg and el.fund == tg.fund:
            pp    = el.parent
            el.setparent(tg)
            elobj = el.dbobj
            
            # And now the database stuff
            if el.isposition:
                if not pp.isfund:
                    pp.dbobj.position.remove(elobj)
                    pp.dbobj.save()
                if not tg.isfund:
                    tg.dbobj.position.add(elobj)
                    tg.dbobj.save()
            else:
                if tg.isfund:
                    elobj.parent = None
                else:
                    elobj.parent = tg.dbobj
                elobj.save()
            self.view.save()
            return el
        else:
            return None
        
    def refresh_me(self):
        '''
        Get the mktrisk
        '''
        self.root.mktrisk
    
