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
    url(r'^lhcbPR/analyse','analyseHome'),
    url(r'^lhcbPR/getFilters', 'getFilters'),
    url(r'^lhcbPR/getJobDetails','getJobDetails'),
    url(r'^lhcbPR/editRequests', 'editRequests'),
    url(r'^lhcbPR/commitClone', 'commitClone'),
    url(r'^lhcbPR/editPanel', 'editPanel'),
    url(r'^lhcbPR/script', 'script'),
    url(r'^lhcbPR/test', 'test')
    
    
    
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)


#urlpatterns += patterns('generic.views',
#    url(r'^generic/$','index'),
#    url(r'^generic/results/$','choose'),
#    url(r'^generic/service/$','handleService'),
#)