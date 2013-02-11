from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView

settings_urls = patterns('rbx.views',
    url(r'^profile$', 'home', name='settings_profile'),
    url(r'^create-team$', 'home', name='settings_create_team'),
)

box_urls = patterns('rbx.views',
    url(r'^$', 'box', name='box'),
    url(r'^/edit$', 'edit_box', name='edit_box'),
)

projects_urls = patterns('rbx.views',
    url(r'^$', 'project', name='project'),
    url(r'^/edit$', 'edit_project', name='edit_project'),
    url(r'^/star$', 'star_project', name='star_project'),
    url(r'^/(?P<box>[\w-]+)', include(box_urls)),
)

urlpatterns = patterns('rbx.views',
    url(r'^$', 'home_or_dashboard', name='home'),
    url(r'^home$', 'home'),
    url(r'^dashboard$', 'dashboard'),
    url(r'^terms$', TemplateView.as_view(template_name="terms.html"),
        name='terms'),
    url(r'^privacy$', TemplateView.as_view(template_name="privacy.html"),
        name='privacy'),
    url(r'^search$', 'home', name='search'),
    url(r'^explore$', 'home', name='explore'),
    url(r'^new$', 'new_project', name='new_project'),
    url(r'^settings/', include(settings_urls)),
    url(r'^(?P<username>\w+)$', 'profile', name='profile'),
    url(r'^(?P<username>\w+)/(?P<project>[\w-]+)', include(projects_urls)),
)
