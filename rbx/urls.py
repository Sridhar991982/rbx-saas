from django.conf.urls.defaults import patterns, url, include

settings_urls = patterns('rbx.views',
    url(r'^profile$', 'home', name='settings_profile'),
)

urlpatterns = patterns('rbx.views',
    url(r'^$', 'home_or_dashboard', name='home'),
    url(r'^home$', 'home'),
    url(r'^dashboard$', 'dashboard'),
    url(r'^signup$', 'signup', name='signup'),
    url(r'^plans$', 'home', name='plans'),
    url(r'^terms$', 'home', name='terms'),
    url(r'^privacy$', 'home', name='privacy'),
    url(r'^search$', 'home', name='search'),
    url(r'^explore$', 'home', name='explore'),
    url(r'^help$', 'home', name='help'),
    url(r'^new$', 'home', name='new_project'),
    url(r'^features$', 'home', name='features'),
    url(r'^settings/', include(settings_urls)),
    url(r'^(?P<username>\w+)$', 'profile', name='profile'),
)
