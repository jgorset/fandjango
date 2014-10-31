try:
    from django.conf.urls.defaults import patterns, url
except:
    from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^authorize_application.html$', authorize_application, name='authorize_application'),
    url(r'^deauthorize_application.html$', deauthorize_application, name='deauthorize_application')
)