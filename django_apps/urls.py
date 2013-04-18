from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^login/$', 'shibsso.views.login'),
    url(r'^logout/$', 'shibsso.views.logout'),
)

urlpatterns += patterns('lhcbPR.views',
    url(r'^$', 'index'),
    url(r'^jobDescriptions/$', 'jobDescriptionsHome'),
    url(r'^jobDescriptions/(?P<app_name>\w+)/$', 'jobDescriptions'),
    url(r'^analyse/$','analyseHome'),
    url(r'^analyse/(?P<analysis_type>\w+)/functions/(?P<function_name>\w+)/(?P<app_name>\w+)/$', 'analysis_extras'),
    url(r'^analyse/(?P<analysis_type>\w+)/results/(?P<app_name>\w+)/$', 'analysis_function'),
    url(r'^analyse/(?P<app_name>\w+)/$', 'analysis_application'),
    url(r'^analyse/(?P<analysis_type>\w+)/(?P<app_name>\w+)/$', 'analysis_render'),
    url(r'^getFilters/$', 'getFilters'),
    url(r'^getJobDetails','getJobDetails'),
    url(r'^commitClone', 'commitClone'),
    url(r'^editPanel', 'editPanel'),
    url(r'^script', 'script'),
    url(r'^test','test'),
    url(r'^newjobdescription', 'new_job_description'),
    url(r'^getcontent', 'get_content')
)
