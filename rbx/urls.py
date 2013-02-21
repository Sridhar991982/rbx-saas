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

profile_url = patterns('rbx.views',
    url(r'^$', 'profile', name='profile'),
    url(r'^/follow$', 'follow_user', name='follow'),
    url(r'^/(?P<project>[\w-]+)', include(projects_urls)),
)

run_urls = patterns('rbx.views',
    url(r'^start$', 'set_run_status', {'status': 'Running'}, name='start_run'),
    url(r'^abort$', 'set_run_status', {'status': 'Aborted'}, name='abort_run'),
    url(r'^cancel$', 'set_run_status', {'status': 'Cancelled'}, name='cancel_run'),
    url(r'^succeeded$', 'set_run_status', {'status': 'Succeeded'}, name='run_succeeded'),
    url(r'^failed$', 'set_run_status', {'status': 'Failed'}, name='run_failed'),
    url(r'^save$', 'save_data', name='save_data'),
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
    url(r'^run/(?P<secret>[a-f0-9-]+)/', include(run_urls)),
    url(r'^(?P<username>\w+)', include(profile_url)),
)
