from django.contrib import admin
from models import FeedProvider, Feed, Post

class FeedProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'link')

class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'provider', 'tags', 'last_modified', 'last_checked', 'etag')
    search_fields = ('name', 'title')

class PostAdmin(admin.ModelAdmin):
    list_display = ('feed', 'title', 'date_created', 'date_modified', 'tags')
    search_fields = ('title', 'content', 'tags')

admin.site.register(FeedProvider, FeedProviderAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Post, PostAdmin)