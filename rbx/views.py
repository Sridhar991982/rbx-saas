from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from actstream import action
from actstream.models import user_stream, actor_stream

from rbx.forms import HomeSignupForm, NewProjectForm
from rbx.models import Project


def home_or_dashboard(request):
    if request.user.is_authenticated():
        return dashboard(request)
    return home(request)


def home(request):
    return render(request, 'home.html', {
        'signup_form': HomeSignupForm,
    })


@login_required
def dashboard(request):
    stream = user_stream(request.user.get_profile())
    return render(request, 'dashboard.html', {
        'stream': stream,
    })


def signup(request, from_home=False):
    return render(request, 'signup.html')


def profile(request, username):
    try:
        user = User.objects.get(username=username)
        stream = actor_stream(user.get_profile())
    except User.DoesNotExist:
        raise Http404
    return render(request, 'profile.html', {
        'stream': stream,
        'user': user,
    })


@login_required
def new_project(request):
    error_occured = False
    if request.method == 'POST':
        form = NewProjectForm(request.POST, user=request.user.get_profile())
        if form.is_valid():
            project_slug = slugify(form.cleaned_data['name'])
            try:
                project = Project(
                    slug=project_slug,
                    name=form.cleaned_data['name'],
                    owner=form.cleaned_data['owner'],
                    public=form.cleaned_data['visibility'] is 'public'
                )
                project.save()
            except Exception:
                error_occured = True
            else:
                return HttpResponseRedirect(reverse('project',
                    args=[form.cleaned_data['owner'], project_slug]))
    else:
        form = NewProjectForm(user=request.user.get_profile())
    return render(request, 'new_project.html', {
        'create_project_form': form,
        'error_occured': error_occured,
    })


def project(request, username, project):
    try:
        project = Project.objects.get(
            owner=User.objects.get(username=username).get_profile(),
            slug=project
        )
    except Project.DoesNotExist:
        raise Http404
    return render(request, 'project.html', {
        'project': project,
    })
