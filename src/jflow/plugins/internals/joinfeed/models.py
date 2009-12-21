from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
 
from tagging.fields import TagField
from tagging.managers import ModelTaggedItemManager

TITLE_MAX_LENGTH = 255
GUID_MAX_LENGTH = 400


class FeedProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    link = models.URLField(verify_exists=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)


class Feed(models.Model):
    name     = models.CharField(_('name'), max_length = 100, editable = False)
    link     = models.URLField(_('feed url'), unique = True)
    title    = models.CharField(_('title'), max_length=200, blank=True, editable = False)
    provider = models.ForeignKey(FeedProvider, null = True, blank = True)
    
    etag          = models.CharField(_('etag'), max_length=50, blank=True, editable = False)
    last_modified = models.DateTimeField(_('last modified'), null=True, blank=True, editable = False)
    last_checked  = models.DateTimeField(_('last checked'), null=True, blank=True, editable = False)
    
    tags          = TagField()
    
    class Meta:
        ordering = ('provider','title',)
    
    def __unicode__(self):
        return self.title or self.name
    
    def clear(self):
        '''
        clear all posts from this feed and set it to initial state
        '''
        posts = Post.objects.filter(feed = self).delete()
        self.last_checked = None
        self.last_modified = None
        self.etag = ''
        self.save()

    
class Post(models.Model):
    feed          = models.ForeignKey(Feed, verbose_name=_('feed'))
    title         = models.CharField(_('title'), max_length=TITLE_MAX_LENGTH)
    link          = models.URLField(_('link'), )
    content       = models.TextField(_('content'), blank=True)
    guid          = models.CharField(_('guid'), max_length=400)
    author        = models.CharField(_('author'), max_length=50, blank=True)
    author_email  = models.EmailField(_('author email'), blank=True)
    comments      = models.URLField(_('comments'), blank=True)
    date_created  = models.DateField(_('date created'), auto_now_add=True)
    date_modified = models.DateTimeField(_('date modified'), null=True, blank=True)
    tags          = TagField()
    
    objects       = ModelTaggedItemManager()

    class Meta:
        verbose_name        = 'Feed post'
        verbose_name_plural = 'Feed posts'
        get_latest_by       = "date_modified"
        ordering            = ('-date_modified',)
        unique_together     = (('feed', 'guid'),)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return self.link
    
    def __get_description(self):
        return self.content
    description = property(fget = __get_description)
    
    def timeordate(self):
        dte = datetime.now()
        td  = dte - self.date_modified
        if not td.days:
            secs  = td.seconds
            mins  = int(secs/60)
            hours = int(mins/60)
            tms   = ''
            link  = ''
            if hours:
                mins -= 60*hours
                if hours == 1:
                    tms = '1 hour'
                else:
                    tms = '%s hours' % hours
                link = ' and '
            if mins > 1:
                tms = '%s%s %s minutes ago' % (tms,link,mins)
            if not tms:
                tms = '1 minute ago'
            return tms
        else:   
            return str(self.date_modified)
