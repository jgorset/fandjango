from django.conf import settings
from django.core.management import call_command

settings.configure(
    DATABASES = {
        'default': {
            'ENGINE': 'sqlite3',
            'NAME': ':memory:'
        }
    },
    INSTALLED_APPS = [
        'fandjango',
        'south',
        'tests.app'
    ],
    ROOT_URLCONF = 'tests.app.urls',
    MIDDLEWARE_CLASSES = [
        'fandjango.middleware.FacebookMiddleware'
    ],
    FACEBOOK_APPLICATION_ID = 181259711925270,
    FACEBOOK_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b',
    FACEBOOK_APPLICATION_NAMESPACE = 'fandjango-test'
)

call_command('syncdb')
call_command('migrate')
