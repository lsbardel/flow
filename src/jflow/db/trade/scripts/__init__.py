

__all__ = ['createTrade']



def createTrade(**kwargs):
    from tflow.models import Trade
    T = Trade(**kwargs)
    T.save()
    try:
        N  = 12
        id = T.id
        cod = '%s0000000000' % Trade.suffix
        sid = str(id)
        cod = '%s%s' % (cod[:N-len(sid)],sid)
        T.code = cod
        T.save()
    except:
        T.delete()
    return T