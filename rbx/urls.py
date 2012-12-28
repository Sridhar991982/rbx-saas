from django.conf.urls.defaults import patterns

urlpatterns = patterns('rbx.views',
    (r'^$', 'home_or_dashboard'),
    (r'^home$', 'home'),
    (r'^dashboard$', 'dashboard'),
)
