from django.conf.urls.defaults import *

from views import home, places

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^places$', places, name='places'),
    
    url('fandjango/', include('fandjango.urls'))
)
