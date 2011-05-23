import os
import django.core.management

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.mock_django.settings'
django.core.management.call_command('syncdb')
