from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/$', 'shibsso.views.login'),
    url(r'^lhcbPR/logout/$', 'shibsso.views.logout'),
)

urlpatterns += patterns('lhcbPR.views',
    url(r'^lhcbPR/$', 'index'),
    url(r'^lhcbPR/jobDescriptions/$', 'jobDescriptionsHome'),
    url(r'^lhcbPR/jobDescriptions/(?P<app_name>\w+)/$', 'jobDescriptions'),
    url(r'^lhcbPR/getFilters', 'getFilters'),
    url(r'^lhcbPR/test', 'test'),
    url(r'^lhcbPR/addnew/', 'addnew'),
    #url(r'^lhcbPR/newdata/$', 'newdata'),
    #url(r'^lhcbPR/newdata/service', 'handleRequest'),
    #url(r'^lhcbPR/newdata/getFilters', 'getFilters'),
    
)

urlpatterns += patterns('generic.views',
    url(r'^generic/$','index'),
    url(r'^generic/results/$','choose'),
    url(r'^generic/service/$','handleService'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)