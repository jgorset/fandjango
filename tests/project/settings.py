DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': ':memory:'
    }
}

MIDDLEWARE_CLASSES = [
    'fandjango.middleware.FacebookMiddleware'
]

INSTALLED_APPS = [
    'fandjango',
    'south',
    'tests.project.app'
]

ROOT_URLCONF = 'tests.project.urls'

FACEBOOK_APPLICATION_ID = 181259711925270
FACEBOOK_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b'
FACEBOOK_APPLICATION_NAMESPACE = 'fandjango-test'
FACEBOOK_APPLICATION_CANVAS_URL = 'http://example.org/foo'