FACEBOOK_APPLICATION_ID = 181259711925270
FACEBOOK_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b'
FACEBOOK_APPLICATION_URL = 'http://apps.facebook.com/fandjango-test'

INSTALLED_APPS = [
    'fandjango'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}