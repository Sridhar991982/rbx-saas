from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from actstream.models import user_stream, actor_stream, followers, following, \
    target_stream

from settings import EDIT_RIGHT
from rbx.forms import RequestInviteForm, NewProjectForm, EditProjectForm
from rbx.models import Project, UserProfile, ProjectRight, Box, Run


def home_or_dashboard(request):
    if request.user.is_authenticated():
        return dashboard(request)
    return home(request)


def home(request):
    if request.method == 'POST':
        form = RequestInviteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Invitation request successfully ' +
                                          'submitted')
            except Exception:
                messages.error(request, 'Oops, something wrong happened, ' +
                                        'please try again...')
    else:
        form = RequestInviteForm()
    return render(request, 'home.html', {
        'request_invite': form,
    })


@login_required
def dashboard(request):
    stream = user_stream(request.user.get_profile())
    projects = Project.objects.filter(
                owner=request.user.get_profile).order_by('-created')
    return render(request, 'dashboard.html', {
        'stream': stream,
        'projects': projects,
    })


def profile(request, username):
    try:
        user = User.objects.get(username=username)
        stream = actor_stream(user.get_profile())
        projects = Project.objects.filter(owner=user).order_by('-created')
        user = user.get_profile()
        user.nb_followers = len(followers(user))
        user.nb_starred = len(following(user, Project))
        user.nb_following = len(following(user, UserProfile))
    except User.DoesNotExist:
        raise Http404
    return render(request, 'profile.html', {
        'stream': stream,
        'profile': user,
        'projects': projects,
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
                    public=form.cleaned_data['visibility'] == 'public'
                )
                project.save()
            except Exception:
                error_occured = True
            else:
                return HttpResponseRedirect(reverse('project',  args=[
                    form.cleaned_data['owner'].user.username, project_slug]))
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
        if not project.is_allowed(request.user.get_profile()):
            raise Http404
        project.co_authors = [project.owner]
        project.co_authors.extend([r.user for r in ProjectRight.objects.filter(
                                    project=project, type__gte=EDIT_RIGHT)])
        project.stargazers = followers(project)
        project.boxes = Box.objects.filter(project=project)
        project.activity = target_stream(project)
        project.all_runs = Run.objects.filter(box__in=project.boxes)
        project.user_runs = project.all_runs.filter(
                                user=request.user.get_profile())
    except Project.DoesNotExist:
        raise Http404
    return render(request, 'project.html', {
        'project': project,
    })


def edit_project(request, username, project):
    status = 'edit'
    try:
        project = Project.objects.get(
            owner=User.objects.get(username=username).get_profile(),
            slug=project
        )
    except Project.DoesNotExist:
        raise Http404
    if not project.is_allowed(request.user.get_profile(), EDIT_RIGHT):
        raise Http404
    project.co_authors = [project.owner]
    project.co_authors.extend([r.user for r in ProjectRight.objects.filter(
                                project=project, type__gte=EDIT_RIGHT)])
    if request.method == 'POST':
        form = EditProjectForm(request.POST, instance=project)
        if form.is_valid():
            try:
                form.save()
                status = 'saved'
            except Exception:
                status = 'error'
    else:
        form = EditProjectForm(instance=project)
    return render(request, 'edit_project.html', {
        'project': project,
        'edit_form': form,
        'status': status,
    })
