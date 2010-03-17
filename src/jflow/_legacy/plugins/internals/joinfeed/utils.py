from datetime import datetime
import time

import feedparser

from models import Feed, Post, TITLE_MAX_LENGTH, GUID_MAX_LENGTH
from settings import FEED_AGGREGATOR_AGENT


def mtime(ttime):
    """ datetime auxiliar function.
    """
    return datetime.fromtimestamp(time.mktime(ttime))

def update(log = None, force = False):
    '''
    Update all feeds and return a list of new posts
    '''
    feeds = Feed.objects.all()
    newposts = []
    for f in feeds:
        ps = updatefeed(f, log, force = force)
        newposts.extend(ps)
    return newposts

def updatefeed(f, log = None, force = False):
    '''
    Update a feed. If force is set to true a scan of the feed is performed, otherwise
    etag or modified are used to reduce bandwidth
    '''
    f.last_checked = datetime.now()
        
    if force:
        f.etag = ''
        f.last_modified = None
            
    etag = f.etag or ''
    last_modified = f.last_modified
            
    kwargs = {}
    if etag:
        kwargs = {'etag': etag}
    elif last_modified:
        ts     = last_modified.timetuple()
        kwargs = {'modified': ts}
    
    try:
        feeddata = feedparser.parse(f.link, agent=FEED_AGGREGATOR_AGENT, **kwargs)
    except:
        log.msg('Feed %s cannot be parsed' % f)
    
    status = feeddata.get('status',None)
    if status:
        # No changes
        if status == 304:
            log.msg('Feed %s unchanged' % f)
            return []

        if status >= 400:
            # http error, ignore
            log.msg('Feed %s HTTP_ERROR: %s' % (f,status));
            return []
    
    bozo  = feeddata.get('bozo',None)
    if bozo:
        log.msg('Feed %s not well formed' % f)
    
    feed          = feeddata.get('feed',None)
    if not feed:
        return []
        
    last_modified = feeddata.get('modified',None)
    if last_modified:
        f.last_modified = mtime(last_modified)
    else:
        f.last_modified = None
        return []
        
    etag  = feeddata.get('etag',None) or ''
    title = feed.get('title',f.link)
    if len(etag) > 50:
        log.msg('Etag for feed %s too long' % f)
        etag = ''
    title = title[:200]
    name  = title[:100]
        
    f.etag  = etag
    f.title = title
    f.name  = name
    
    try:
        f.save()
    except Exception, e:
        log.msg('Unhandled exception while saving feed %s: %s' % (f,e))
        return []
    
    np =  updatefeedposts(f, feeddata, log)
    log.msg('Feed %s added %s posts' % (f,len(np)))
    return np
    
    
    
def updatefeedposts(f, feeddata, log):
    last_modified = f.last_modified
    feed     = feeddata.feed
    posts    = feeddata.entries
    tags     = f.tags
        
    newposts = []
    for p in posts:
        try:
            link = p.get('link',None)
            
            # No link or link too long skip the post
            if not link or len(link) > 200:
                continue
            
            guid = p.get('guid',link)
            if len(guid) > GUID_MAX_LENGTH:
                log.msg('GUID too long for Post %s' % link)
                continue
            ps   = Post.objects.filter(feed = f, guid = guid)
            #
            # New post. Add to DB
            if not ps.count():
                title = p.get('title',link)
                title = title[:TITLE_MAX_LENGTH]
                try:
                    content = p.content[0].value
                except:
                    content = p.get('summary', p.get('description', ''))
                updated = p.get('updated_parsed')
                if not updated:
                    updated = datetime.now()
                else:
                    dp = mtime(updated)
                ps = Post(feed          = f,
                          title         = title,
                          link          = link,
                          content       = content,
                          guid          = guid,
                          tags          = tags,
                          date_modified = dp)
                ps.save()
                log.msg('Added post %s' % ps)
                newposts.append(ps)
        except Exception, e:
            log.msg('Unhandled exception while processing feed-post %s: %s' % (ps,e))
        
    return newposts


def clearnews():
    '''
    Delete all news post and set Feed last_checked and last_modified to None
    '''
    feeds = Feed.objects.all()
    for f in feeds:
        f.clear()
    