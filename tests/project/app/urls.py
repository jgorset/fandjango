from django.conf.urls import *

from views import home, places, redirect

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^places$', places, name='places'),
    url(r'^redirect$', redirect, name='redirect'),

    url('fandjango/', include('fandjango.urls'))
)
