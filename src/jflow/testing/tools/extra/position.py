from django.db.models import Q

from loadermsg import loadermsg


def livepositions(dt, fund = None):
    from jflow.db.trade.models import Position
    pos = Position.objects.filter(
                                  Q(status__gt = 0),
                                  Q(open_date__lte  = dt),
                                  Q(close_date__gte = dt) | Q(close_date__isnull=True)
                                  )
    if fund:
        return pos.filter(fund = fund)
    else:
        return pos

class closepositions(loadermsg):
    
    def __init__(self,*args,**kwargs):
        super(closepositions,self).__init__(*args,**kwargs)
        
    def handle(self):
        from jflow.db.trade.models import Position
        cd = self.logdate()
        if cd == None:
            return
        pos = Position.objects.filter(
                                      Q(status__gt = 0),
                                      Q(open_date__lte = cd),
                                      Q(close_date__gt = cd) | Q(close_date__isnull=True)
                                      )
        for p in pos:
            hist = p.positionhistory_set.all()
            lasthist = hist.latest()
            dt = lasthist.dt
            #
            # Last history date less than currenct loading date.
            # Here we close the position
            if dt < cd:
                p.close_date = dt
                p.save() 
            
            
        