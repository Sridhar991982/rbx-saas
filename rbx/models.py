import os
import xmlrpclib
import xml.etree.cElementTree as etree
from haystack import indexes
from haystack import site
from hashlib import sha1
from datetime import datetime, timedelta, date
from django.db import models
from django.http import Http404
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from settings import VIEW_RIGHT, EDIT_RIGHT, ADMIN_RIGHT, \
    CLOUD_ENDPOINT, CLOUD_AUTH, PUBLIC_KEY, STORAGE, RESULT_URL, VM_SRC, SITE_URL
from actstream.models import followers, following, target_stream, user_stream, actor_stream

PROJECT_RIGHT = (
    (VIEW_RIGHT, 'View'),
    (EDIT_RIGHT, 'Edit'),
    (ADMIN_RIGHT, 'Admin'),
)

EXECUTOR_SOURCE_TYPE = (
    ('git', 'Git'),
    ('hg', 'Mercurial'),
    ('svn', 'Subversion'),
    ('xz', 'Gzipped tar archive'),
    ('xj', 'Bzipped tar archive'),
    ('zip', 'Zip archive'),
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
NIC = [ network_uname=oneadmin,network = "%(network)s" ]
GRAPHICS = [
port = "-1",
type = "vnc"
]
CONTEXT = [
public_key = "%(ssh_key)s",
%(context)s
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
        contribute = ProjectRight.objects.filter(user=self).filter(right__gte=EDIT_RIGHT)
        user_projects.extend([c.project for c in contribute])
        return user_projects

    def followers(self):
        return followers(self.user, User)

    def starred(self):
        return following(self.user, Project)

    def following(self):
        return following(self.user, User)

    def stream(self):
        return user_stream(self.user)

    def activity(self):
        return actor_stream(self.user)

    def runs(self):
        return Run.objects.filter(user=self).order_by('-launched')

    def stats(self):
        stats = {}
        total_runs = self.runs()
        today = date.today()
        start_week = today - timedelta(today.weekday())
        end_week = start_week + timedelta(7)
        week_runs = total_runs.filter(launched__range=[start_week, end_week])
        stats['total_runs'] = len(total_runs)
        stats['total_time'] = total_runs.filter(status__gt=4).aggregate(Avg('duration'))['duration__avg'] or 0
        stats['week_runs'] = len(week_runs)
        stats['week_time'] = week_runs.filter(status__gt=4).aggregate(Avg('duration'))['duration__avg'] or 0
        return stats

    def link(self):
        return reverse('profile', args=[self.user.username])


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
        return target_stream(self, '')

    def boxes(self):
        return Box.objects.filter(project=self)

    def runs(self):
        return Run.objects.filter(box__in=self.box_set.iterator()).order_by('-launched')

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
        return '%s %s\'s %s right' % (self.user, self.project.name, self.permission(''))

    def rights(self):
        return PROJECT_RIGHT

    def permission(self, prefix='Can '):
        for idx, right in PROJECT_RIGHT:
            if self.right == idx:
                return '%s%s' % (prefix, right.lower())

    def delete_right(self):
        return reverse('project_rights_delete',
                       args=[self.project.owner.user.username,
                             self.project.slug,
                             self.user.user.username])


class System(models.Model):
    identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Box(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    name = models.SlugField(max_length=30, db_index=True)
    description = models.TextField(blank=True)
    source_location = models.CharField(max_length=255)
    source_type = models.CharField(choices=EXECUTOR_SOURCE_TYPE,
                                   default=EXECUTOR_SOURCE_TYPE[0][0],
                                   max_length=20)
    system = models.ForeignKey(System)
    before_run = models.CharField(max_length=255, blank=True)
    run_command = models.CharField(max_length=255)
    after_run = models.CharField(max_length=255, blank=True)
    lifetime = models.PositiveSmallIntegerField()
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

    def runs(self, user=None):
        return Run.objects.filter(box=self).order_by('-launched')

    def get_sources(self):
        if self.source_type in ('hg', 'git'):
            return '%s clone %s %s' % (self.source_type,
                                       self.source_location,
                                       VM_SRC)
        if self.source_type == 'svn':
            return 'svn checkout %s %s' % (self.source_location, VM_SRC)
        if self.source_type in ('xz', 'xj'):
            return 'mkdir -p %s && curl %s | tar %s -C %s' % (VM_SRC,
                                                              self.source_location,
                                                              self.source_type,
                                                              VM_SRC)
        if self.source_type == 'zip':
            return 'cd /tmp && curl %s -o src.zip && unzip src.zip -d %s' % (self.source_location,
                                                                             VM_SRC)

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
    started = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=RUN_STATUS, default=1)
    secret_key = models.CharField(max_length=36)
    vm_id = models.PositiveSmallIntegerField(null=True, blank=True)
    lifetime = models.PositiveSmallIntegerField(default=5)

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
        return 0

    def set_status(self, name):
        idx = self.get_status_id(name)
        if idx in (2, 3):
            self.stop(idx)
        elif idx == 4 and self.status < 4:
            self.started = datetime.now()
        elif idx > 4 and self.status < 5:
            self.duration = (datetime.now() - self.started).total_seconds()
            self.stop(idx)
        self.status = idx
        self.save()

    def start(self, network='private'):
        # XXX: Check if user is not over quota
        success, vm_id, _ = self.rpc.one.vm.allocate(
            CLOUD_AUTH,
            VM_TEMPLATE % {'image': self.box.system.identifier,
                           'network': network,
                           'ssh_key': PUBLIC_KEY,
                           'context': self.context()})
        if success:
            self.status = 1
            self.vm_id = vm_id
        else:
            self.status = 0
        self.save()
        if not success:
            raise Exception()

    def context(self):
        return 'rbx_launch="%s",' % os.path.join(SITE_URL,
                                                 reverse('run_script',
                                                         args=[self.secret_key]))

    def stop(self, reason):
        if self.vm_id:
            self.rpc.one.vm.action(CLOUD_AUTH, 'finalize', self.vm_id)

    def state(self):
        info = self._info(self.vm_id)
        vm_state = int(info.find('STATE').text)
        states = ['init', 'pending', 'hold', 'active', 'stopped',
                  'suspended', 'done', 'failed']
        lcm_states = ['lcm_init', 'prolog', 'boot', 'running', 'migrate',
                      'save_stop', 'save_suspend', 'save_migrate', 'prolog_migrate',
                      'prolog_resume', 'epilog_stop', 'epilog', 'shutdown',
                      'cancel', 'failure', 'delete', 'unknown']
        if states[vm_state] == 'active':
            state = int(info.find('LCM_STATE').text)
            return lcm_states[state]
        return states[vm_state]

    def ip(self):
        return self._info(self.vm_id).find('TEMPLATE/NIC').find('IP').text

    def is_finished(self):
        return self.status not in (1, 4)

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

    def outputs(self):
        output_dir = os.path.join(STORAGE, RESULT_URL, self.storage())
        if not os.path.isdir(output_dir):
            return []
        return [os.path.join(RESULT_URL, self.storage(), f)
                for f in os.listdir(output_dir)]

    def storage(self):
        return sha1(str(self.pk) + str(self.launched) + str(self.user)).hexdigest()

    def params(self):
        return RunParam.objects.filter(run=self).order_by('box_param__order')

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


class UserProfileIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def index_queryset(self):
        return UserProfile.objects.filter(user__date_joined__lte=datetime.now())



class ProjectIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    owner = indexes.CharField(model_attr='owner')
    created = indexes.DateTimeField(model_attr='created')
    updated = indexes.DateTimeField(model_attr='updated')
    description = indexes.CharField(model_attr='description')

    def index_queryset(self):
        return Project.objects.filter(created__lte=datetime.now())


site.register(UserProfile, UserProfileIndex)
site.register(Project, ProjectIndex)
