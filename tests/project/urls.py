from django.conf.urls import *

urlpatterns = patterns('',
    (r'^', include('tests.project.app.urls'))
)
