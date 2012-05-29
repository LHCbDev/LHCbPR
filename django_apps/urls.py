from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('generic.views',
    url(r'^generic/$','index'),
    url(r'^generic/results/$','choose'),
    url(r'^generic/service/$','handleService'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
