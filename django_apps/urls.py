from django.conf.urls.defaults import patterns, include, url
from django.views.generic import DetailView, ListView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('algo.views',
    url(r'^algos/$','compare_page'),
    url(r'^algos/results','compare_page_results'),
    url(r'^algos/history','history'),
    url(r'algos/wut', 'dictTest')
)

urlpatterns += patterns('genplot.views',
    url(r'^genplot/$','index'),
    url(r'^genplot/results/$','choose'),
    url(r'^genplot/service/$','handleService'),
)

urlpatterns += patterns('generic.views',
    url(r'^generic/$','index'),
    url(r'^generic/results/$','choose'),
    url(r'^generic/service/$','handleService'),
)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
)


###########################################################
#url(r'^add_data/','algo.views.add'),
#url(r'^save_file/$','algo.views.save_file'),
#url(r'^algos/(?P<page_num>\d+)/$','algo.views.prints_num')
