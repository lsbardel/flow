from datetime import datetime

from atomformat import Feed

from models import Post

class PostFeed(Feed):
    feed_id          = "my_id"
    feed_title       = "Quantmind News Aggregator"
    feed_description = "Latest post at quantmind"
    
    def __init__(self, *args, **kwargs):
        self.numfeeds = kwargs.pop('numfeeds',20)
        
    def feed_updated(self, feed):
        item = Post.objects.latest()
        return item.date_modified
    
    def item_id(self, post):
        return '.'
    
    def item_title(self, post):
        return post.title
    
    def item_updated(self, post):
        return post.date_modified
    
    def item_published(self, post):
        return post.date_modified
    
    def item_authors(self, post):
        feeds = [post.feed]
        for feed in feeds:
            yield {'name': feed.title}
            
    def item_content(self, item):
        content_dict = {}
        content_dict['type'] = 'html'
        content     = ['<div>',
                       item.feed.title,
                       '</div>',
                       '<div>',
                       item.content,
                       '</div>']
        content_text = '\n'.join(content)
        return (content_dict,content_text)
        
    def item_links(self, item):
        return [{'href':item.link}]
    
    def items(self):
        feeds = Post.objects.all()
        N = feeds.count()
        if N:
            N = min(N,self.numfeeds) - 1
            return feeds[:N]
        else:
            return []