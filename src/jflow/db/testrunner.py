from django.test.simple import DjangoTestSuiteRunner
from django.contrib.contenttypes.models import ContentType



class JflowTestSuiteRunner(DjangoTestSuiteRunner):
    
    def setup_databases(self, **kwargs):
        old_names, mirrors = super(JflowTestSuiteRunner,self).setup_databases(**kwargs)
        ContentType.objects.all().delete()
        from django.core.management import call_command
        call_command('loaddata', 'content_types', verbosity=self.verbosity)
        return old_names, mirrors