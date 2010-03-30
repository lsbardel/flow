from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

class Command(BaseCommand):
    
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models

        format  = options.get('format','json')
        exclude = options.get('exclude',[])
        show_traceback = options.get('traceback', False)
        path           = options.get('filename','dbdata')
        compression    = options.get('comp','zip')

        excluded_apps = [get_app(app_label) for app_label in exclude]

        if len(app_labels) == 0:
            app_list = [app for app in get_apps() if app not in excluded_apps]
        else:
            app_list = [get_app(app_label) for app_label in app_labels]

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)

        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)

        object_count = 0
        objects = []
        mod     = 'wb'
        import gzip
        for app in app_list:
            for model in get_models(app):
                meta       = model._meta
                app_label  = meta.app_label
                model_name = meta.module_name
                gname      = '%s/%s.%s.%s.gz' % (path,app_label,model_name,format)
                file = gzip.GzipFile(gname, mod)
                #mod  = 'ab'
                objects = model._default_manager.all()
                try:
                    data = serializers.serialize(format, objects)
                except Exception, e:
                    if show_traceback:
                        raise
                    raise CommandError("Unable to serialize database: %s" % e)
                object_count += objects.count()
                file.write(data)
                file.close()
                
        print 'Dumped %s objects' % object_count
        #if compression == 'zip':
        #    import zlib
        #    data = zlib.compress(data)
        #f = open(filename,'w')
        #f.write(data)
        #f.close()
        
        
