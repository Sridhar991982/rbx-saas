from datetime import datetime, timedelta, date
from django.db import models
from django.http import Http404
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from settings import VIEW_RIGHT, EDIT_RIGHT, ADMIN_RIGHT, \
    CLOUD_ENDPOINT, CLOUD_AUTH, PUBLIC_KEY
from actstream.models import followers, following, target_stream
import xmlrpclib
import xml.etree.cElementTree as etree

PROJECT_RIGHT = (
    (VIEW_RIGHT, 'View'),
    (EDIT_RIGHT, 'Edit'),
    (ADMIN_RIGHT, 'Admin'),
)

EXECUTOR_SOURCE_TYPE = (
    ('git', 'Git'),
    ('hg', 'Mercurial'),
    ('git svn', 'Subversion'),
)

RUN_STATUS = (
    (0, 'Error'),
    (1, 'Pending'),
    (2, 'Aborted'),
    (3, 'Cancelled'),
    (4, 'Running'),
    (5, 'Succeeded'),
    (6, 'Failed'),
)

VM_TEMPLATE = '''
CPU = 1
VCPU = 1
MEMORY = 2048
RANK = "- RUNNING_VMS"
DISK = [
source   = "%(image)s",
target   = "hda",
save     = no,
readonly = "no",
driver = "raw"
]
DISK = [
type     = swap,
size     = 2048,
target   = "hdb",
readonly = "no"
]
NIC = [ network_uname=oneadmin,network = "public" ]
GRAPHICS = [
port = "-1",
type = "vnc"
]
CONTEXT = [
public_key = "%(ssh_key)s",
%(params)s
target = "hdd"
]
'''


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    gravatar_email = models.EmailField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        if self.user.get_full_name():
            return '%s (%s)' % (self.user.get_full_name(), self.user.username)
        return self.user.username

    def gravatar(self):
        return self.gravatar_email or self.user.email

    def projects(self):
        user_projects = list(Project.objects.filter(owner=self))
        contribute = ProjectRight.objects.filter(user=self).filter(right=EDIT_RIGHT)
        user_projects.extend([c.project for c in contribute])
        return user_projects

    def followers(self):
        return followers(self)

    def starred(self):
        return following(self, Project)

    def following(self):
        return following(self, UserProfile)

    def stream(self):
        #user_stream(request.user.get_profile())
        return None

    def activity(self):
        #actor_stream(user.get_profile())
        return None

    def runs(self):
        return Run.objects.filter(user=self)

    def stats(self):
        stats = {}
        total_runs = self.runs()
        today = date.today()
        start_week = today - timedelta(today.weekday())
        end_week = start_week + timedelta(7)
        week_runs = total_runs.filter(started__range=[start_week, end_week])
        stats['total_runs'] = len(total_runs)
        stats['total_time'] = total_runs.filter(status__gt=4).aggregate(Avg('duration'))['duration__avg'] or 0
        stats['week_runs'] = len(week_runs)
        stats['week_time'] = week_runs.filter(status__gt=4).aggregate(Avg('duration'))['duration__avg'] or 0
        return stats


class Project(models.Model):
    slug = models.SlugField(db_index=True)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(UserProfile, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s project' % self.name

    def is_allowed(self, user, right=VIEW_RIGHT):
        if not self.public and not user.is_authenticated():
            return False
        if self.public and right == VIEW_RIGHT:
            return True
        if not user.is_authenticated() and right != VIEW_RIGHT:
            return False
        if self.owner == user.get_profile():
            return True
        try:
            authorized = ProjectRight.objects.get(user=user.get_profile(), project=self)
        except ProjectRight.DoesNotExist:
            return False
        return authorized.right >= right

    def link(self, anchor=None):
        anchor = anchor and '#/' + anchor or ''
        return reverse('project', args=[self.owner.user.username, self.slug]) + anchor

    def edit_link(self):
        return reverse('edit_project', args=[self.owner.user.username, self.slug])

    def star_link(self):
        return reverse('star_project', args=[self.owner.user.username, self.slug])

    def rights_link(self):
        return reverse('project_rights', args=[self.owner.user.username, self.slug])

    def authors(self):
        authors = [self.owner]
        authors.extend([r.user for r in
                        ProjectRight.objects.filter(project=self,
                                                    right__gte=EDIT_RIGHT)])
        return authors

    def stargazers(self):
        return followers(self)

    def activity(self):
        return target_stream(self)

    def boxes(self):
        return Box.objects.filter(project=self)

    def runs(self, user=None):
        if user is not None and not user.is_authenticated():
            return None
        project_runs = Run.objects.filter(box__in=self.box_set.iterator()).order_by('-launched')
        if user:
            return project_runs.filter(user=user.get_profile())[:10]
        return project_runs[:10]

    @staticmethod
    def retrieve(username, project_slug, user, right=VIEW_RIGHT):
        owner = get_object_or_404(User, username=username).get_profile()
        project = get_object_or_404(Project, owner=owner, slug=project_slug)
        if not project.is_allowed(user, right):
            raise Http404
        return project

    class Meta:
        unique_together = ('owner', 'slug')


class ProjectRight(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    user = models.ForeignKey(UserProfile, db_index=True)
    right = models.PositiveSmallIntegerField(choices=PROJECT_RIGHT,
                                             max_length=20)

    def __unicode__(self):
        return '%s\'s %s right' % (self.right, self.project.name)

    def rights(self):
        return PROJECT_RIGHT

    def permission(self):
        for idx, right in PROJECT_RIGHT:
            if self.right == idx:
                return 'Can %s' % right.lower()

    def delete_right(self):
        return reverse('project_rights_delete',
                       args=[self.project.owner.user.username,
                             self.project.slug,
                             self.user.user.username])


class OperatingSystem(models.Model):
    identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Box(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    name = models.SlugField(max_length=30, db_index=True)
    description = models.TextField(blank=True)
    source_repository = models.CharField(max_length=255)
    repository_type = models.CharField(choices=EXECUTOR_SOURCE_TYPE, max_length=20)
    os = models.ForeignKey(OperatingSystem)
    before_run = models.CharField(max_length=255, blank=True)
    run_command = models.CharField(max_length=255)
    after_run = models.CharField(max_length=255, blank=True)
    lifetime = models.PositiveSmallIntegerField(default=3)
    allow_runs = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s\'s %s box' % (self.project.name, self.name)

    def link(self, anchor=None):
        anchor = anchor and '#/' + anchor or ''
        return reverse('box', args=[self.project.owner.user.username,
                                    self.project.slug,
                                    self.name]) + anchor

    def edit_link(self):
        return reverse('edit_box', args=[self.project.owner.user.username,
                                         self.project.slug,
                                         self.name])

    def avg_duration(self):
        return Run.objects.filter(box=self,
                                  status__gt=4).aggregate(Avg('duration'))['duration__avg']

    @staticmethod
    def retrieve(username, project_slug, box_name, user, right=VIEW_RIGHT):
        project = Project.retrieve(username, project_slug, user, right)
        return get_object_or_404(Box, project=project, name=box_name)

    class Meta:
        unique_together = ('project', 'name')
        verbose_name_plural = 'boxes'


class BoxParam(models.Model):
    name = models.SlugField()
    box = models.ForeignKey(Box)
    field_type = models.CharField(max_length=32)
    subtype = models.CharField(max_length=32)
    constraints = models.TextField()
    order = models.PositiveSmallIntegerField()
    css_class = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return '%s\'s %s box param' % (self.box.project.name, self.name)


class Run(models.Model):
    box = models.ForeignKey(Box)
    user = models.ForeignKey(UserProfile)
    launched = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True)
    duration = models.FloatField(null=True)
    status = models.PositiveSmallIntegerField(choices=RUN_STATUS, default=1)
    secret_key = models.CharField(max_length=36)
    vm_id = models.PositiveSmallIntegerField(null=True)

    def __unicode__(self):
        return '%s\'s run #%d' % (self.box.project.name, self.id)

    @property
    def rpc(self):
        if not hasattr(self, '_rpc'):
            self._rpc = xmlrpclib.ServerProxy(CLOUD_ENDPOINT)
        return self._rpc

    def get_status_id(self, name):
        for idx, status in RUN_STATUS:
            if status.lower() == name.lower():
                return idx
        raise Exception('Status name not found')

    def set_status(self, name):
        idx = self.get_status_id(name)
        if self.status == idx:
            return
        self.status = idx
        if idx == 4:
            self.started = datetime.now()
        elif idx > 4:
            self.duration = (datetime.now() - self.started).total_seconds()
        self.save()

    def start(self):
        # XXX: Check if user is not over quota
        success, vm_id, _ = self.rpc.one.vm.allocate(
            CLOUD_AUTH,
            VM_TEMPLATE % {'image': self.box.os.identifier,
                           'ssh_key': PUBLIC_KEY,
                           'params': self.box_context_params() + self.run_context_params()})
        self.vm_id = vm_id
        if not success:
            self.status = 0
        self.save()
        if not success:
            raise Exception()

    def box_context_params(self):
        params = 'rbx_clone="%s clone %s %s",\n' % (self.box.repository_type,
                                                    self.box.source_repository,
                                                    self.box.name)
        params += 'rbx_box_name="%s",\n' % self.box.name
        params += 'rbx_before_run="%s",\n' % self.box.before_run
        params += 'rbx_run_cmd="%s",\n' % self.box.run_command
        params += 'rbx_after_run="%s",\n' % self.box.after_run
        return params

    def run_context_params(self):
        return ''

    def stop(self, reason):
        self.rpc.one.vm.action(CLOUD_AUTH, 'finalize', self.vm_id)
        self.status = reason

    def state(self):
        info = self._info(self.vm_id)
        # TODO: Parse XML state

    def ip(self):
        return self._info(self.vm_id).find('TEMPLATE/NIC').find('IP').text

    def _info(self, xml=True):
        success, info, _ = self.rpc.one.vm.info(CLOUD_AUTH, self.vm_id)
        return xml and etree.fromstring(info.encode('utf-8')) or info

    def status_text(self):
        for idx, status in RUN_STATUS:
            if self.status == idx:
                return status

    def link(self):
        return reverse('box', args=[self.user.user.username,
                                    self.box.project.slug,
                                    self.box.name])

    class Meta:
        get_latest_by = 'launched'


class RunParam(models.Model):
    run = models.ForeignKey(Run, db_index=True)
    box_param = models.ForeignKey(BoxParam)
    value = models.TextField()

    def __unicode__(self):
        return '%s run #%d\'s %s' % (self.run.box.project.name,
                                     self.id,
                                     self.box_param.name)


class Invitation(models.Model):
    email = models.EmailField()
    request_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Invitation request: %s' % self.email
