from django.conf.urls.defaults import url, include, patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login$', 'django.contrib.auth.views.login', {
        'template_name': 'login.html',
    }, name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
    }, name='logout'),
    url(r'', include('rbx.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
