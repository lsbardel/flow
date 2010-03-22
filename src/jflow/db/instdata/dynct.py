from django import forms
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import modelform_factory


class ExtraContentModel(models.Model):
    '''
    Abstract Model class for models with a dynamic content_type
    The content_type field must be implemented by derived classes
    '''
    #content_type   = models.ForeignKey(ContentType, blank=True, null=True)
    object_id      = models.PositiveIntegerField(default = 0, editable = False)
    _extra_content = generic.GenericForeignKey('content_type', 'object_id')
    
    def __init__(self, *args, **kwargs):
        super(ExtraContentModel,self).__init__(*args, **kwargs)
        self._new_content = None
    
    class Meta:
        abstract = True
        
    def extra_content(self):
        try:
            return self._extra_content
        except:
            return None
    
    @property
    def type(self):
        if self.content_type:
            return self.content_type.name
        else:
            return ''
        
    def _denormalize(self, ec = None):
        pass
        
    def save(self, **kwargs):
        nc = self._new_content
        if nc:
            ec = self.extra_content()
            if ec and ec != nc:
                ec.delete()
            self.content_type = ContentType.objects.get_for_model(nc)
            if nc.id:
                self.object_id = nc.id
        if not self.object_id:
            self.object_id = 0
        super(ExtraContentModel,self).save(**kwargs)
        if nc:
            self._denormalize()
            nc.save()
            if self.object_id != nc.id:
                self.object_id = nc.id
                super(ExtraContentModel,self).save(**kwargs)
        self._extra_content = nc
        


class ExtraContentForm(forms.ModelForm):
    '''
    This model form handles extra content from a content type field
    The model must be an instance of ExtraContentModel
    '''    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance',None)
        if instance:
            pre_content = instance.extra_content()
        else:
            pre_content = None
        super(ExtraContentForm,self).__init__(*args, **kwargs)
        kwargs['instance'] = pre_content
        self.content_form = self.get_content_form(*args, **kwargs)
        
    def is_valid(self):
        vi = super(ExtraContentForm,self).is_valid()
        if self.content_form:
            vi = self.content_form.is_valid() and vi
            if vi:
                self.cleaned_data.update(self.content_form.cleaned_data)
            else:
                self.errors.update(self.content_form.errors)
        return vi
    
    def get_content_form(self, *args, **kwargs):
        ct = self.instance.content_type
        data = dict(self.data.items())
        ctt  = data.get('content_type',self.initial.get('content_type',None))
        if ctt:
            ct = ContentType.objects.get(id = int(ctt))
        if ct:
            pre_content   = kwargs.pop('instance',None)
            content_model = ct.model_class()
            if isinstance(pre_content,content_model):
                kwargs['instance'] = pre_content 
            content_form  = modelform_factory(content_model)
            return content_form(*args, **kwargs)
        else:
            return None
    
    def save(self, commit = True):
        obj = super(ExtraContentForm,self).save(commit = False)
        if self.content_form:
            obj._denormalize(self.content_form.instance)
            obj._new_content = self.content_form.save(commit = False)
        return super(ExtraContentForm,self).save(commit = commit)
    