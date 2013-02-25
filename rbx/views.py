from os import makedirs
from json import dumps
from os.path import join, isdir
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from actstream.actions import is_following, follow, unfollow
from uuid import uuid4

from settings import STORAGE, EDIT_RIGHT
from rbx.forms import RequestInviteForm, NewProjectForm, EditProjectForm, \
    BoxForm, RunForm, ParamForm
from rbx.models import Project, Box, Run, BoxParam


def home_or_dashboard(request):
    return request.user.is_authenticated() and dashboard(request) or home(request)


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
    return render(request, 'dashboard.html')


def profile(request, username):
    user = get_object_or_404(User, username=username).get_profile()
    return render(request, 'profile.html', {'profile': user})


@login_required
def follow_user(request, username):
    user = get_object_or_404(User, username=username).get_profile()
    if user == request.user.get_profile():
        return
    if is_following(request.user.get_profile(), user):
        unfollow(request.user.get_profile(), user)
    else:
        follow(request.user.get_profile(), user, actor_only=False)
    return HttpResponseRedirect(reverse('profile', args=[username]))


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
    project = Project.retrieve(username, project, request.user)
    if request.method == 'POST':
        box_form = BoxForm(request.POST,
                           project=project,
                           form_class='well',
                           initial={'project': project},
                           action=project.link())
        if box_form.is_valid():
            try:
                new_box = box_form.save()
                messages.success(request, '%s box successfully saved' % new_box.name)
                return HttpResponseRedirect(new_box.link())
            except Exception:
                messages.error(request, 'Oops, something wrong happened, please try again...')
                return HttpResponseRedirect(project.link())
    else:
        box_form = BoxForm(project=project,
                           form_class='well',
                           initial={'project': project},
                           action=project.link('boxes'))
    return render(request, 'project.html', {
        'project': project,
        'box_error': request.method == 'POST',
        'box_form': box_form,
    })


@login_required
def edit_project(request, username, project):
    status = 'edit'
    project = Project.retrieve(username, project, request.user, EDIT_RIGHT)
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
    project = Project.retrieve(username, project, request.user)
    if is_following(request.user.get_profile(), project):
        unfollow(request.user.get_profile(), project)
    else:
        follow(request.user.get_profile(), project, actor_only=False)
    return HttpResponseRedirect(project.link())


def box(request, username, project, box):
    box = Box.retrieve(username, project, box, request.user)
    if request.method == 'POST' and request.user.is_authenticated():
        launch = RunForm(request.POST, box=box, user=request.user)
        if launch.is_valid():
            try:
                run = Run(box=box,
                          user=request.user.get_profile(),
                          status=1,
                          secret_key=str(uuid4()))
                run.save()
                run.start()
            except Exception:
                messages.error(request, 'Oops, something wrong happened, please try again...')
    else:
        launch = RunForm(box=box, user=request.user)
    return render(request, 'box.html', {
        'box': box,
        'launch': launch,
    })


@login_required
def edit_box(request, username, project, box):
    status = 'edit'
    box = Box.retrieve(username, project, box, request.user, EDIT_RIGHT)
    if request.method == 'POST':
        form = BoxForm(request.POST,
                       instance=box,
                       action=box.edit_link(),
                       project=box.project)
        if form.is_valid():
            try:
                form.save()
                status = 'saved'
            except Exception:
                status = 'error'
    else:
        form = BoxForm(instance=box,
                       project=box.project,
                       action=box.edit_link())
    return render(request, 'edit_box.html', {
        'box': box,
        'edit_form': form,
        'status': status,
    })


@login_required
def param_form(request, username, project, box, param_type=None, param_id=None):
    box = Box.retrieve(username, project, box, request.user, EDIT_RIGHT)
    param = None
    new = None
    success = False
    if param_id:
        try:
            param = BoxParam.objects.get(pk=param_id)
        except BoxParam.DoesNotExist:
            return HttpResponse('Your request returned no results.')
    else:
        if param_type not in ('text', 'number'):
            return HttpResponse('Your request cannot be completed.')
        new = param_type
    if request.method == 'POST':
        form = ParamForm(request.POST, new=new, param=param, box=box, action=request.path)
        if form.is_valid():
            args = {'name': form.cleaned_data.pop('parameter_name'),
                    'box': form.cleaned_data.pop('box'),
                    'subtype': form.cleaned_data.pop('subtype'),
                    'field_type': form.cleaned_data.pop('type'),
                    'order': form.cleaned_data.pop('order')}
            args['constraints'] = dumps(form.cleaned_data)
            BoxParam(**args).save()
            success = True
        else:
            print(form.errors)
    else:
        form = ParamForm(new=new, param=param, box=box, action=request.path)
    return render(request, 'param.html', {'form': form, 'success': success})


def set_run_status(request, secret, status):
    run = get_object_or_404(Run, secret_key=secret)
    run.set_status(status)
    return HttpResponse('{status: 0}')


@csrf_exempt
def save_data(request, secret):
    run = get_object_or_404(Run, secret_key=secret)
    if request.method == 'POST':
        if not 'title' in request.POST or not 'file' in request.FILES:
            return HttpResponse('{status: 2}')
        location = join(STORAGE, str(run.pk))
        if not isdir(location):
            makedirs(location)
        with open(join(location, request.POST['title']), 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        return HttpResponse('{status: 0}')
    return HttpResponse('{status: 1}')
