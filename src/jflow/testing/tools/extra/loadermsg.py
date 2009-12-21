from datetime import date


class loadermsg(object):
    
    def __init__(self, user, error_class_name = None):
        self.user         = user
        self.content_type = None
        self.rel_date     = None
        self.html         = None
        self.error_class_name = error_class_name or 'error_message'
        self.allmsg  = []
        
    def logdate(self):
        if self.rel_date:
            return self.rel_date
        else:
            return date.today()
        
    def saverror(self, e):
        self.allmsg.append((False,'%s' % e))
    
    def saveok(self, el):
        self.allmsg.append((True,'%s successfully processed' % el))
        
    def as_html(self):
        from django.utils.safestring import mark_safe
        if self.html:
            return self.html
        
        li = []
        li.append('<p>Processed %s elements.</p>' % len(self.allmsg))
        n = 0
        ne = 0
        le = []
        for ok,msg in self.allmsg:
            n += 1
            if ok:
                le.append('<p>%s - %s</p>' % (n,msg))
            else:
                ne += 1
                le.append('<p class="%s">%s - %s</p>' % (self.error_class_name,n,msg))
        if ne:
            li.append('<p class="%s">Number of failures: %s</p>:' % (self.error_class_name,ne))
        li.extend(le)
        self.html = mark_safe(u'\n'.join(li))
        return self.html
    
    def wrapload(self):
        self.handle()
        try:
            from jflow.db.report.models import Logger
            msg = self.as_html()
            ct  = self.content_type
            if ct:
                dt = self.logdate()
                l = Logger.objects.filter(relevant_date = dt, content_type = ct)
                if not l.count():
                    l = Logger(relevant_date = dt, content_type = ct)
                else:
                    l = l[0]
                l.message = u'%s' % msg
                l.save()
        except:
            pass
            
    def handle(self):
        pass

