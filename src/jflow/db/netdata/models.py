import platform

from django.db import models

from jflow.conf import settings


class ServerMachineManager(models.Manager):
    
    def get_for_machine(self, code):
        machine = platform.node()
        try:
            return self.get(code = code, machine = machine)
        except:
            return None
        
    def save_for_machine(self, code, url):
        el = self.get_for_machine(code)
        if el:
            el.url = url
        else:
            el = self.model(code = code, url = url, machine = platform.node())
        el.save()
        return el        
        

class ServerMachine(models.Model):
    code    = models.CharField(max_length = 200, default = 'jflow-rpc')
    machine = models.CharField(max_length = 200)
    url     = models.CharField(max_length = 200, default = 'http://localhost:%s' % settings.RPC_SERVER_PORT)
    
    objects = ServerMachineManager()
    
    class Meta:
        unique_together = ('code','machine')
    
    def __unicode__(self):
        return '%s - %s - %s' % (self.code,self.machine,self.url)
    
    def get_proxy(self):
        from unuk.core.jsonrpc import Proxy
        return Proxy(self.url)
    
    def get_info(self):
        proxy = self.get_proxy()
        try:
            return proxy.info()
        except IOError:
            return [{'name':'connection','value':'Not available'}]