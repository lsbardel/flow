from django.db.models import signals

from jflow.db.instdata.models import DataId


def delete_instrument(dataid, **kwargs):
    instrument = dataid.instrument
    if instrument:
        instrument.delete()

signals.pre_delete.connect(delete_instrument, sender=DataId)