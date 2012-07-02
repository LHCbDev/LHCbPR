from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
#    url(r'^accounts/login/$', 'shibsso.views.login'),
#    url(r'^accounts/logout/$', 'shibsso.views.logout'),
#    url(r'^login/$', 'shibsso.views.login'),
#    url(r'^logout/$', 'shibsso.views.logout'),
    url(r'^lhcbPR/login/$', 'shibsso.views.login'),
    url(r'^lhcbPR/logout/$', 'shibsso.views.logout'),
)

urlpatterns += patterns('lhcbPR.views',
    url(r'^lhcbPR/$', 'index'),
    url(r'^lhcbPR/newdata', 'newdata'),
    url(r'^lhcbPR/service', 'handleRequest'),
    url(r'^lhcbPR/test', 'test'),
    url(r'^lhcbPR/addnew', 'addnew'),
    url(r'^lhcbPR/getFilters', 'getFilters')
)

urlpatterns += patterns('generic.views',
    url(r'^generic/$','index'),
    url(r'^generic/results/$','choose'),
    url(r'^generic/service/$','handleService'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)