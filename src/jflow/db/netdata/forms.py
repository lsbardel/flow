import platform

from django import forms

from jflow.db.netdata.models import ServerMachine

class ServerForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if not instance:
            initial = kwargs.get('initial',None) or {}
            initial['machine'] = platform.node()
            kwargs['initial'] = initial
        super(ServerForm,self).__init__(*args, **kwargs)
        
    class Meta:
        model = ServerMachine
        
    def save(self, commit = True):
        if commit:
            cd = self.instance
            server = ServerMachine.objects.filter(machine = cd.machine, code = cd.code)
            if server:
                server = server[0]
                server.url = cd.url
                self.instance = server
        return super(ServerForm,self).save(commit)
    
    