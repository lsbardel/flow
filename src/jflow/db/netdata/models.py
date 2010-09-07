import platform

from django.db import models


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
    code    = models.CharField(max_length = 200)
    machine = models.CharField(max_length = 200)
    url     = models.CharField(max_length = 200)
    
    objects = ServerMachineManager()
    
    class Meta:
        unique_together = ('code','machine')
    
    