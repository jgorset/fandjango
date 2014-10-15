DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

INSTALLED_APPS = [
    'fandjango',
    'south',
    'tests.project.app'
]

SOUTH_TESTS_MIGRATE = False
SOUTH_MIGRATION_MODULES = {
    'fandjango': 'fandjango.south_migrations',
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tests.project.urls'

FACEBOOK_APPLICATION_ID = 181259711925270
FACEBOOK_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b'
FACEBOOK_APPLICATION_NAMESPACE = 'fandjango-test'
FACEBOOK_APPLICATION_CANVAS_URL = 'http://example.org/foo'

SECRET_KEY = '123'

USE_TZ = True

DEBUG = True
