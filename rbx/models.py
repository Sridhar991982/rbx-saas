from django.db import models
from django.contrib.auth.models import User


PROJECT_RIGHT = (
    ('view', 'View'),
    ('edit', 'Edit'),
)

PROJECT_FIELD = (
    ('input', 'Inline input'),
    ('textarea', 'Multiline text area'),
)

EXECUTOR_SOURCE_TYPE = (
    ('gzip', 'GZIP archive'),
    ('git', 'Git repository'),
    ('hg', 'Mercurial repository'),
    ('svn', 'Subversion repository'),
)

EXECUTOR_PARAM_TYPE = (
    ('string', 'String'),
    ('text', 'Text'),
    ('int', 'Integer'),
)

BUILD_STATUS = (
    ('success', 'Success'),
    ('failed', 'Failed'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    company = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    gravatar_email = models.EmailField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        if self.user.get_full_name():
            return '%s (%s)' % (self.user.get_full_name(), self.user.username)
        return self.user.username

    def gravatar(self):
        return self.gravatar_email or self.user.email


class Project(models.Model):
    slug = models.SlugField(db_index=True)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(UserProfile, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s project' % self.name

    class Meta:
        unique_together = ('owner', 'slug')


class ProjectRight(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    user = models.ForeignKey(UserProfile, db_index=True)
    type = models.CharField(choices=PROJECT_RIGHT, max_length=20)

    def __unicode__(self):
        return '%s\'s %s right' % (self.type, self.project.name)

    def can_edit(self):
        return self.type == 'edit'


class ProjectField(models.Model):
    slug = models.SlugField(db_index=True)
    project = models.ForeignKey(Project, db_index=True)
    name = models.CharField(max_length=50)
    value = models.TextField()
    type = models.CharField(choices=PROJECT_FIELD, max_length=20)
    order = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return '%s\'s %s' % (self.project.name, self.name)


class Executor(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    description = models.TextField()
    source = models.CharField(max_length=255)
    source_type = models.CharField(choices=EXECUTOR_SOURCE_TYPE, max_length=20)
    language = models.CharField(max_length=40)
    install = models.CharField(max_length=255)
    script = models.CharField(max_length=255)
    after_script = models.CharField(max_length=255)
    after_failure = models.CharField(max_length=255)
    after_success = models.CharField(max_length=255)
    lifetime = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return '%s\'s executor' % self.project.name


class ExecutorParam(models.Model):
    slug = models.SlugField(db_index=True)
    executor = models.ForeignKey(Executor, db_index=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=30, choices=EXECUTOR_PARAM_TYPE)
    required = models.BooleanField(default=True)
    activated = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s\'s %s executor' % (self.project.name, self.name)


class Build(models.Model):
    executor = models.ForeignKey(Executor)
    user = models.ForeignKey(UserProfile)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField()

    def __unicode__(self):
        return '%s\'s build #%d' % (self.executor.project.name, self.id)


class BuildParam(models.Model):
    build = models.ForeignKey(Build, db_index=True)
    executor_param = models.ForeignKey(ExecutorParam, db_index=True)
    value = models.TextField()

    def __unicode__(self):
        return '%s build #%d\'s %s' % (self.build.executor.project.name,
                                       self.id,
                                       self.executor_param.name)
