import datetime

import base

__all__ = ['futurecurve']


class futurecurve(base.compositeFactory):

    def __init__(self, contract = None, yccode = None, *args, **kwargs):
        super(futurecurve,self).__init__(*args, **kwargs)
        self.yccode = yccode
        if contract:
            from prospero import db
            self.contract = db.get_future_contract(contract)
            self.codeco   = '%s%s' % (self.contract.code,self.klasscode)
        
    def _make(self, dte, holder):
        from prospero import db
        from prospero.contrib.instrument.factory import get_tools
        co   = self.contract
        tols = get_tools()
        dtef = dte
        if dtef == None:
            dtef = datetime.date.today()
        nc   = max(co.term_structure,1)
        futs = db.get_futures(co, first_notice__gt = dtef)
        
        curveKlass = None
        if co.asset_class == tols.fi_asset_class():
            if co.instrument_type == tols.imm3mirf():
                curveKlass = RATES.yc
            else:
                curveKlass = None
        else:
            curveKlass = RATES.convenienceComposite
        
        ra = curveKlass(code = self.codeco, dte = dte)
        scalar_rate_class = ra.scalar_rate_class
        
        for f in futs:
            id   = db.get_id(f.data_id)
            inst = f.make_position()
            sr   = self.get_scalar(id, dte, scalar_rate_class, inst = inst, holder = holder)
            ra.add(sr)
        return ra
        
    
