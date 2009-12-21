

from cashflow import *

class sparselem(object):
    
    def __init__(self,row,col,elem):
        self.row = row
        self.col = col
        self.elem = elem
        
    def cash(self):
        return self.elem.cash()
    
    def __str__(self):
        return '[%s,%s] = %s' % (self.row,self.col,self.elem)
    
    def __repr__(self):
        return str(self)
    

class sparsecf(object):
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.elems = []
        
    def __repr__(self):
        return str(self.elems)
    
    def __str__(self):
        return self.__repr__()
        
    def append(self,row,col,v):
        self.elems.append(sparselem(row,col,v))
        
    def fill(self, mat):
        mat.fill(0)
        elems = self.elems
        for el in elems:
            mat[el.row,el.col] += el.cash()
        return mat
        
    

class CashFlowMatrix(CashFlowBase):
    '''
    Cash flow matrix object.
    This object contains an ordered list of CashFlow objects.
    '''
    def __init__(self):
        CashFlowBase.__init__(self, False)
        self.drhs        = None
        self.trhs        = None
        self.lowertriang = True
        
    def clear(self):
        self.trhs = None
        
    def add(self, cfs):
        '''
        Add cash flow to the cash flow matrix
        '''
        if not isinstance(cfs,CashFlow):
            return
        
        endte = cfs.enddate
        inner = self.inner
        try:
            inner.add(endte,cfs)
        except:
            self.lowertriang = False
            raise NotImplementederror, "not implemented"
        
    def refresh(self, dcf):
        if self.trhs == None:
            self.build(dcf)
        return self.getmatrices()
        
    def daterhs(self):
        '''
        Build the dates for the right-hand site matrix
        '''
        rhs = InnerCF()
        for cfs in self.itervalues():
            for kv in cfs:
                dte = kv.key
                cf  = kv.value
                if not self.has_date(dte):
                    try:
                        rhs.add(dte,None)
                    except:
                        pass
        return rhs
            
    def build(self, dcf):
        from qmpy.lib.math import lowertriang, rqmatrix
        if len(self) == 0:
            self.lhs = None
            self.rhs = None
            return
        
        drhs  = self.daterhs()
        outer = self.inner
        N     = len(outer)
        K     = len(drhs)
        lhs   = sparsecf(N,N)
        rhs   = sparsecf(N,K)
        row   = 0
        for cfs in self.itervalues():
            for kv in cfs:
                dte = kv.key
                cf  = kv.value
                if drhs.has_key(dte):
                    col = drhs.index(dte)[0]
                    rhs.append(row,col,cf)
                else:
                    col = outer.index(dte)[0]
                    lhs.append(row,col,cf)
            row += 1
        self.lhs = lhs
        self.rhs = rhs
        trhs = rqmatrix(K)
        k = 0
        for d in drhs:
            trhs[k] = dcf(d.key)
        self.trhs = trhs
            
        
    def getmatrices(self):
        from qmpy.lib.core import lowertriang, rqmatrix
        trhs  = self.trhs
        if trhs == None:
            return None,None,None
    
        lhs   = self.lhs
        rhs   = self.rhs
        N     = lhs.rows
        K     = rhs.cols
        if self.lowertriang:
            LHS   = lowertriang(N)
        else:
            LHS   = rqmatrix(N,N)
        RHS   = rqmatrix(N,K)
        lhs.fill(LHS)
        rhs.fill(RHS)
        return LHS,RHS,trhs
        
    
    