from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.db.models import Avg, Count
from actstream.models import user_stream, actor_stream, followers, following, \
    target_stream
from actstream.actions import follow, unfollow, is_following

from settings import EDIT_RIGHT
from rbx.forms import RequestInviteForm, NewProjectForm, EditProjectForm, \
    BoxForm
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
    stream = None #user_stream(request.user.get_profile())
    projects = Project.objects.filter(
                owner=request.user.get_profile).order_by('-created')
    return render(request, 'dashboard.html', {
        'stream': stream,
        'projects': projects,
    })


def profile(request, username):
    try:
        user = User.objects.get(username=username)
        stream = None #actor_stream(user.get_profile())
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
                messages.error(request, 'Oops, something wrong happened, ' +
                                        'please try again...')
            else:
                return HttpResponseRedirect(reverse('project',  args=[
                    form.cleaned_data['owner'].user.username, project_slug]))
    else:
        form = NewProjectForm(user=request.user.get_profile())
    return render(request, 'new_project.html', {
        'create_project_form': form,
    })


def project(request, username, project):
    owner = User.objects.get(username=username).get_profile()
    project = get_object_or_404(Project, owner=owner, slug=project)
    if not project.is_allowed(request.user.get_profile()):
        raise Http404
    project.boxes = Box.objects.filter(project=project)
    project.all_runs = Run.objects.filter(box__in=project.boxes)
    project.user_runs = project.all_runs.filter(
                            user=request.user.get_profile())

    project.boxes.annotate(nb_runs=Count('run'))

    if request.method == 'POST':
        box_form = BoxForm(request.POST, project=project, form_class='well',
                            initial={'project': project}, action=project.link())
        if box_form.is_valid():
            try:
                box_form.save()
                messages.success(request, '%s box successfully saved'
                        % box_form.cleaned_data['name'].title())
                return HttpResponseRedirect(reverse('box',
                        args=(project.owner.user.username,
                            project.slug, box_form.cleaned_data['name'])))
            except Exception:
                messages.error(request, 'Oops, something wrong happened,' +
                                        ' please try again...')
                return HttpResponseRedirect(reverse('project',
                        args=(project.owner.user.username,
                            project.slug)))
    else:
        box_form = BoxForm(project=project, form_class='well',
                            initial={'project': project}, action=project.link('boxes'))
    return render(request, 'project.html', {
        'project': project,
        'box_error': request.method == 'POST',
        'box_form': box_form,
    })

@login_required
def edit_project(request, username, project):
    status = 'edit'
    owner = User.objects.get(username=username).get_profile()
    project = get_object_or_404(Project, owner=owner, slug=project)
    if not project.is_allowed(request.user.get_profile(), EDIT_RIGHT):
        raise Http404
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


@login_required
def star_project(request, username, project):
    try:
        project = Project.objects.get(
            owner=User.objects.get(username=username).get_profile(),
            slug=project
        )
        if not project.is_allowed(request.user.get_profile()):
            raise Http404
        if is_following(request.user.get_profile(), project):
            unfollow(request.user.get_profile(), project)
        else:
            follow(request.user.get_profile(), project, actor_only=False)
    except Project.DoesNotExist:
        raise Http404
    except:
        raise
    return HttpResponseRedirect(reverse('project',
                args=(project.owner.user.username,
                      project.slug)))


def box(request, username, project, box):
    owner = User.objects.get(username=username).get_profile()
    project = get_object_or_404(Project, owner=owner, slug=project)
    box = get_object_or_404(Box, project=project, name=box)
    return render(request, 'box.html', {
        'box': box,
    })

@login_required
def edit_box(request, username, project, box):
    status = 'edit'
    owner = User.objects.get(username=username).get_profile()
    project = get_object_or_404(Project, owner=owner, slug=project)
    box = get_object_or_404(Box, project=project, name=box)
    if not project.is_allowed(request.user.get_profile(), EDIT_RIGHT):
        raise Http404
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box, action=box.edit_link(),
                       project=project, initial={'project': project})
        if form.is_valid():
            try:
                form.save()
                status = 'saved'
            except Exception:
                status = 'error'
    else:
        form = BoxForm(instance=box, project=project, action=box.edit_link(),
                        initial={'project': project})
    return render(request, 'edit_box.html', {
        'box': box,
        'edit_form': form,
        'status': status,
    })
