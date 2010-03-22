import datetime

from manip import Position, PositionHistory, POSITION_STATUS_SYNCRONIZED

__all__ = ['position_from_size_and_price']



def create_position(**kwargs):
    fund  = kwargs.pop('fund')
    ic    = kwargs.pop('instrument')
    open_date = kwargs.pop('open_date',None) or datetime.date.today()
    status    = kwargs.pop('status',POSITION_STATUS_SYNCRONIZED)
    return Position.objects.get_or_create_position(fund,
                                                   open_date,
                                                   ic,
                                                   status = status)

def position_from_size_and_price(**kwargs):
    po    = create_position(**kwargs)
    size  = kwargs.pop('size')
    price = kwargs.pop('price')
    fins  = po.instrumentCode.instrument()
    h = PositionHistory.objects.predate(po, dt = po.open_date)
    # Position is a new one
    if not h:
        h = PositionHistory(position = po,
                            dt       = po.open_date,
                            size     = size,
                            value    = price)
        h.save()
    else:
        h = h[0]
    return h

