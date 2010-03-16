from django.contrib.contenttypes.models import ContentType

from tagging.managers import ModelTaggedItemManager


class DataIdManager(ModelTaggedItemManager):
    
    def for_type(self, type):
        app_label = self.model._meta.app_label
        try:
            ct = ContentType.objects.get(name = type, app_label = app_label)
        except:
            return self.Empty()
        return self.filter(content_type = ct)
        
        