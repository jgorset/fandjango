from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^', include('tests.project.app.urls'))
)
