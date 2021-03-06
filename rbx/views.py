from os import makedirs
from json import dumps
from os.path import join, isdir, basename
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

from settings import STORAGE, VIEW_RIGHT, EDIT_RIGHT, ADMIN_RIGHT, COMMON_ERROR_MSG, \
    RESULT_URL, SITE_URL, VM_SRC
from rbx.forms import RequestInviteForm, NewProjectForm, EditProjectForm, \
    BoxForm, RunForm, ParamForm, ProfileForm, PasswordForm
from rbx.models import Project, Box, Run, BoxParam, RunParam, UserProfile, ProjectRight, \
    Software, System


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
    running = len(request.user.get_profile().runs().filter(status__in=[1, 4]))
    return render(request, 'dashboard.html', {'stats': request.user.get_profile().stats(),
                                              'running': running})


def profile(request, username):
    user = get_object_or_404(User, username=username).get_profile()
    return render(request, 'profile.html', {'profile': user})


@login_required
def profile_settings(request):
    user = User.objects.get(username=request.user)
    if request.method == 'POST' and 'update_password' in request.POST:
        password_form = PasswordForm(request.POST, username=request.user)
        if password_form.is_valid():
            try:
                user.set_password(password_form.cleaned_data['new_password'])
                user.save()
                messages.success(request, 'Password successfully updated')
            except:
                messages.error(request, COMMON_ERROR_MSG)
            return HttpResponseRedirect(reverse('settings_profile'))
    else:
        password_form = PasswordForm(username=request.user)
    if request.method == 'POST' and'update_profile' in request.POST:
        profile_form = ProfileForm(request.POST, profile=request.user.get_profile())
        if profile_form.is_valid():
            try:
                user.first_name = profile_form.cleaned_data.pop('full_name')
                user.save()
                profile = user.get_profile()
                for field, value in profile_form.cleaned_data.items():
                    setattr(profile, field, value)
                profile.save()
                messages.success(request, 'Profile successfully updated')
            except:
                messages.error(request, COMMON_ERROR_MSG)
            return HttpResponseRedirect(reverse('settings_profile'))
    else:
        profile_form = ProfileForm(profile=request.user.get_profile())
    return render(request, 'profile_settings.html', {'profile_form': profile_form,
                                                     'password_form': password_form,
                                                     'stats': user.get_profile().stats()})


@login_required
def follow_user(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        if is_following(request.user, user):
            unfollow(request.user, user)
        else:
            follow(request.user, user, actor_only=False)
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
                           action=project.link('boxes'))
        if box_form.is_valid():
            try:
                new_box = box_form.save()
                messages.success(request, '%s box successfully saved' % new_box.name)
                return HttpResponseRedirect(new_box.link())
            except:
                messages.error(request, COMMON_ERROR_MSG)
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
    if is_following(request.user, project):
        unfollow(request.user, project)
    else:
        follow(request.user, project, actor_only=False)
    return HttpResponseRedirect(project.link())


def box(request, username, project, box):
    run = None
    box = Box.retrieve(username, project, box, request.user)
    if request.method == 'POST' and request.user.is_authenticated():
        launch_form = RunForm(request.POST, box=box, user=request.user)
        if launch_form.is_valid():
            try:
                new_run = Run(box=box,
                              user=request.user.get_profile(),
                              status=1,
                              secret_key=str(uuid4()))
                new_run.lifetime = launch_form.cleaned_data.pop('lifetime')
                new_run.save()
                box_param = BoxParam.objects.filter(box=box)
                for param, value in launch_form.cleaned_data.items():
                    RunParam(value=(value or ''),
                             run=new_run,
                             box_param=box_param.get(name=param)).save()
                new_run.start()
                messages.success(request, 'Run #%s launched successfully' % new_run.pk)
            except Exception:
                messages.error(request, COMMON_ERROR_MSG)
            return HttpResponseRedirect(box.link())
    else:
        launch_form = RunForm(box=box, user=request.user)
        if 'cancel' in request.GET and request.user.is_authenticated():
            try:
                run_id = int(request.GET['cancel'])
                cancelled_run = Run.objects.get(pk=run_id)
                if cancelled_run.user == request.user.get_profile():
                    if cancelled_run.status in (1, 4):
                        cancelled_run.set_status('cancelled')
                    messages.success(request, 'Run #%s cancelled successfully' % run_id)
            except:
                messages.error(request, 'Sorry, we where unable to cancel this run...')
            return HttpResponseRedirect(box.link())
        elif 'run' in request.GET:
            try:
                run_id = int(request.GET['run'])
                run = Run.objects.get(pk=run_id, box=box)
            except:
                messages.error(request, 'Sorry, we where unable to find this run...')
    return render(request, 'box.html', {
        'box': box,
        'launch_form': launch_form,
        'run': run,
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
                    'css_class': form.cleaned_data['type'] == 'number' and 'input-mini' or '',
                    'field_type': form.cleaned_data.pop('type'),
                    'order': form.cleaned_data.pop('order')}
            if 'pk' in form.cleaned_data:
                args['pk'] = form.cleaned_data.pop('pk')
            args['constraints'] = dumps(form.cleaned_data)
            BoxParam(**args).save()
            success = True
    else:
        form = ParamForm(new=new, param=param, box=box, action=request.path)
    return render(request, 'edit_param.html', {'form': form, 'success': success})


@login_required
def delete_param(request, username, project, box, param_id):
    box = Box.retrieve(username, project, box, request.user, EDIT_RIGHT)
    param = get_object_or_404(BoxParam, pk=param_id)
    param.delete()
    return HttpResponse('{status: 0}')


@login_required
def project_rights(request, username, project):
    project = Project.retrieve(username, project, request.user, ADMIN_RIGHT)
    status = None
    if request.method == 'POST':
        right = int(request.POST['right'])
        if right in (VIEW_RIGHT, EDIT_RIGHT, ADMIN_RIGHT):
            status = 'saved'
            try:
                user = UserProfile.objects.get(user__username=request.POST['username'])
                if user != project.owner:
                    project_right = ProjectRight.objects.get(user=user, project=project)
                    project_right.right = right
                    project_right.save()
            except UserProfile.DoesNotExist:
                status = 'notexist'
            except ProjectRight.DoesNotExist:
                project_right = ProjectRight(project=project, user=user, right=right).save()
            except:
                status = 'error'
        else:
            status = 'error'
    return render(request, 'manage_rights.html', {'project': project, 'status': status})


@login_required
def project_rights_delete(request, username, project, user):
    try:
        project = Project.retrieve(username, project, request.user, ADMIN_RIGHT)
        user = UserProfile.objects.get(user__username=user)
        project_right = ProjectRight.objects.get(user=user, project=project)
        project_right.delete()
    except:
        pass
    return HttpResponseRedirect(project.rights_link())


def explore(request):
    projects = {
        'active': None,
        'popular': None,
        'newest': None  # Project.objects.all().order_by('-created')[:5],
    }
    users = {
        'active': None,
        'popular': None,
        'newest': None  # UserProfile.objects.filter(user__is_active=True).order_by('-user__date_joined')[:5],
    }
    return render(request, 'explore.html', {'projects': projects, 'users': users})


def set_run_status(request, secret, status):
    try:
        run = Run.objects.get(secret_key=secret)
        run.set_status(status)
        return HttpResponse('0')
    except Run.DoesNotExist:
        return HttpResponse('1')
    except Exception:
        return HttpResponse('2')


@csrf_exempt
def save_data(request, secret):
    if request.method == 'POST':
        if not 'title' in request.POST or not 'file' in request.FILES:
            return HttpResponse('2')
        try:
            run = Run.objects.get(secret_key=secret)
        except Run.DoesNotExist:
            return HttpResponse('3')
        if run.status != 4:
            return HttpResponse('4')
        location = join(STORAGE, RESULT_URL, run.storage())
        if not isdir(location):
            makedirs(location)
        with open(join(location, basename(request.POST['title'])), 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        return HttpResponse('0')
    return HttpResponse('1')


def run_script(request, secret):
    run = get_object_or_404(Run, secret_key=secret)
    return render(request, 'run.sh', {'site_url': SITE_URL,
                                      'vm_src': VM_SRC,
                                      'run': run},
                  content_type="text/plain")


def system_software(request, system_id):
    try:
        system = System.objects.get(pk=system_id)
        return render(request, 'system_software.html',
                      {'softwares': Software.objects.filter(system=system).order_by('category')})
    except System.DoesNotExist:
        return HttpResponse('<p>No software available</p>')
