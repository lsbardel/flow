from jflow.utils.observer import lazyobject

__all__ = ['lazyrate']

class lazyrate(lazyobject):
    
    def __init__(self,*args,**kwargs):
        super(lazyrate,self).__init__(*args,**kwargs)
        
    def post_attach(self, obs):
        obs.update(self)

