from django.contrib.sitemaps import Sitemap
from models import DataId

class DataSiteMap(Sitemap):
    changefreq = "never"
    priority = 0.5
    
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def items(self):
        return DataId.objects.all()
    
    def location(self, obj):
        return '%s/%s/' % (self.baseurl,obj.code)