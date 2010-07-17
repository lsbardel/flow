from stdnet import orm

from jflow.models import *

def register(**kwargs):
    orm.register(FinIns, **kwargs)
    orm.register(PortfolioHolder, **kwargs)
    orm.register(Portfolio, **kwargs)
    orm.register(Position, **kwargs)
    orm.register(PortfolioView, **kwargs)
    orm.register(PortfolioViewFolder, **kwargs)
    orm.register(UserViewDefault, **kwargs)