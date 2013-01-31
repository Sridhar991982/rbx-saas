from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('doc.views',
    url(r'article/(?P<fileref>[\w.-]+)$', 'article'),
    url(r'report/(?P<fileref>[\w.-]+)$', 'report'),
    url(r'slide/(?P<fileref>[\w.-]+)$', 'slide'),
)
