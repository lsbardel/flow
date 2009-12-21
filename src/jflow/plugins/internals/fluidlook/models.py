from django.db import models

from tagging.fields import TagField



class WebSite():
    tags    = TagField('labels', blank = True, null = True)
    
    
    
    
class SingletonWebSite(models.Model):
    baseurl = models.URLField()
    website = models.ForeignKey(WebSite)
    
    
