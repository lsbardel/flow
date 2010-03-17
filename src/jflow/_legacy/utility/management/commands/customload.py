import os
import gzip
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from optparse import make_option

def clear_contenttype():
    from django.db.models import get_model
    try:
        ContentType = get_model('contenttypes', 'contenttype')
    except:
        return
    ct = ContentType.objects.all()
    for c in ct:
        c.delete()

class Command(BaseCommand):
    
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models
        from django.core import serializers
        from django.db import connection, transaction
        from django.conf import settings
        
        self.style    = no_style()
        
        verbosity     = int(options.get('verbosity', 1))
        path          = options.get('filename','dbdata')
        clearct       = options.get('clearcontent',False)
        models        = set()
        files         = os.listdir(path)
        fixture_count = 0
        object_count  = 0
        
        models        = set()
        
        if clearct:
            clear_contenttype()
        
        cursor = connection.cursor()

        # Start transaction management. All fixtures are installed in a
        # single transaction to ensure that all references are resolved.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        
        for file in files:
            gfile = '%s/%s' % (path,file)
            if os.path.isfile(gfile):
                object_application = 0
                sp    = file.split('.')
                if len(sp) == 4:
                    app_label  = sp[0]
                    model_name = sp[1]
                    format     = sp[2]
                    if verbosity > 2:
                        print "Loading model '%s' for application '%s'" % (model_name,app_label)
                    gfile = gzip.GzipFile(gfile,'rb')
                    data  = gfile.read()
                    fixture_count += 1
                    objects = serializers.deserialize(format, data)
                    try:
                        for obj in objects:
                            object_application += 1
                            models.add(obj.object.__class__)
                            obj.save()
                    except Exception, e:
                        print "model '%s' for application '%s' failed to serialize. Skipping." % (model_name,app_label)
                        continue
                    fixture_count += 1
                    object_count  += object_application
                    if verbosity > 1:
                        print "Loaded %s entries for model '%s.%s'" % (object_application,app_label,model_name)
                    gfile.close()
                else:
                    if verbosity > 1:
                        print "Skipping %s" % gfile
                        
        if object_count > 0:
            sequence_sql = connection.ops.sequence_reset_sql(self.style, models)
            if sequence_sql:
                if verbosity > 1:
                    print "Resetting sequences"
                for line in sequence_sql:
                    cursor.execute(line)            
        
        transaction.commit()
        transaction.leave_transaction_management()

        if object_count == 0:
            if verbosity > 1:
                print "No fixtures found."
        else:
            if verbosity > 0:
                print "Installed %d objects from %d models" % (object_count, fixture_count)
                    
                    