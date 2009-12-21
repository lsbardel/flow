from django.conf import settings

from tagging.models import Tag, TaggedItem

_replacetags = {'defense':'defence'}

_notags = ['and','are',
           'here','have','has',
           'is',
           'or',
           'there','then','than',
           'with','where','which','what']

_splitters = ',.:;&$/\\'


def clean(tag):
    if not tag:
        return None
    for s in _splitters:
        tag = tag.replace(s,' ')
    tags = tag.split(' ')
    rtags = []
    for t in tags:
        if settings.FORCE_LOWERCASE_TAGS:
            t = t.lower()
        l = len(t)
        if l <= 1:
            continue
        if t.endswith('s'):
            if l == 2:
                continue
            tl = t[:-1]
            objs = Tag.objects.filter(name = tl)
            if objs.count():
                continue
        if t not in rtags:
            rtags.append(t)
    return rtags



def cleanalltags():
    tags = Tag.objects.all()
    for t in tags:
        ts = clean(t.name)
        if not ts:
            t.delete()
        elif len(ts) > 1 or ts[0] != t.name:
            tagged = TaggedItem.objects.filter(tag = t)
            t.delete()
            for newname in ts:
                newtag = Tag.objects.filter(name = newname)
                if not newtag:
                    newtag = Tag(name = newname)
                    newtag.save()
                else:
                    newtag = newtag[0]
                    
                for tobj in tagged:
                    obj = tobj.object
                    c = TaggedItem.objects.filter(tag_name = newname,
                                                  content_type = tobj.content_type,
                                                  object_id = tobj.object_id)
                    if not c:
                        c = TaggedItem(tag = newtag,
                                       content_type = tobj.content_type,
                                       object_id = tobj.object_id)
                        c.save()
                        
            
            
        