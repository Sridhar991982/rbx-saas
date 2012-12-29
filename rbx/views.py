from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from rbx.forms import HomeSignupForm, NewProjectForm
from rbx.models import Project


def home_or_dashboard(request):
    return home(request)


def home(request):
    return render(request, 'home.html', {
        'signup_form': HomeSignupForm,
    })


@login_required
def dashboard(request):
    return home(request)


def signup(request, from_home=False):
    return render(request, 'signup.html')


def profile(request, username):
    return home(request)


@login_required
def new_project(request):
    error_occured = False
    if request.method == 'POST':
        form = NewProjectForm(request.POST, user=request.user)
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
        form = NewProjectForm(user=request.user)
    return render(request, 'new_project.html', {
        'create_project_form': form,
        'error_occured': error_occured,
    })


def project(request, username, project):
    try:
        project = Project.objects.get(
            owner=User.objects.get(username=username),
            slug=project
        )
    except Project.DoesNotExist:
        raise Http404
    return render(request, 'project.html', {
        'project': project,
    })
