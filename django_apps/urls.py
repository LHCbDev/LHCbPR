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
    url(r'^lhcbPR/analyse/$','analyseHome'),
    url(r'^lhcbPR/analyse/(?P<app_name>\w+)/$', 'analysis_application'),
    url(r'^lhcbPR/analyse/(?P<analysis_type>\w+)/(?P<app_name>\w+)/$', 'analysis_type'),
    url(r'^lhcbPR/analysis_function/$', 'analysis_function'),
    url(r'^lhcbPR/getFilters/$', 'getFilters'),
    url(r'^lhcbPR/getJobDetails','getJobDetails'),
    url(r'^lhcbPR/commitClone', 'commitClone'),
    url(r'^lhcbPR/editPanel', 'editPanel'),
    url(r'^lhcbPR/script', 'script'),
    url(r'^lhcbPR/upload','upload_file'),
    url(r'^lhcbPR/getRunnedJobs', 'getRunnedJobs'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)