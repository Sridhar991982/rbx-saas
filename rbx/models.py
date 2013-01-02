from django.db import models
from django.contrib.auth.models import User
from settings import VIEW_RIGHT, EDIT_RIGHT, ADMIN_RIGHT


PROJECT_RIGHT = (
    (VIEW_RIGHT, 'View'),
    (EDIT_RIGHT, 'Edit'),
    (ADMIN_RIGHT, 'Admin'),
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
    description = models.TextField(blank=True)
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s project' % self.name

    def is_allowed(self, user, type=VIEW_RIGHT):
        if self.owner == user:
            return True
        if self.public and type == VIEW_RIGHT:
            return True
        try:
            authorized = ProjectRight.objects.get(user=user, project=self)
        except ProjectRight.DoesNotExist:
            return False
        return authorized.type >= type

    class Meta:
        unique_together = ('owner', 'slug')


class ProjectRight(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    user = models.ForeignKey(UserProfile, db_index=True)
    type = models.PositiveSmallIntegerField(choices=PROJECT_RIGHT,
                                            max_length=20)

    def __unicode__(self):
        return '%s\'s %s right' % (self.type, self.project.name)


class Box(models.Model):
    project = models.ForeignKey(Project, db_index=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=255)
    source_type = models.CharField(choices=EXECUTOR_SOURCE_TYPE, max_length=20)
    language = models.CharField(max_length=40)
    install = models.CharField(max_length=255, blank=True)
    script = models.CharField(max_length=255)
    after_script = models.CharField(max_length=255, blank=True)
    after_failure = models.CharField(max_length=255, blank=True)
    after_success = models.CharField(max_length=255, blank=True)
    lifetime = models.PositiveSmallIntegerField(default=8)

    def __unicode__(self):
        return '%s\'s box' % self.project.name

    class Meta:
        verbose_name_plural = 'boxes'


class BoxParam(models.Model):
    slug = models.SlugField(db_index=True)
    box = models.ForeignKey(Box, db_index=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=30, choices=EXECUTOR_PARAM_TYPE)
    required = models.BooleanField(default=True)
    activated = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s\'s %s box param' % (self.box.project.name, self.name)


class Run(models.Model):
    box = models.ForeignKey(Box)
    user = models.ForeignKey(UserProfile)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField()

    def __unicode__(self):
        return '%s\'s run #%d' % (self.box.project.name, self.id)


class RunParam(models.Model):
    run = models.ForeignKey(Run, db_index=True)
    box_param = models.ForeignKey(BoxParam, db_index=True)
    value = models.TextField()

    def __unicode__(self):
        return '%s run #%d\'s %s' % (self.run.box.project.name,
                                     self.id,
                                     self.box_param.name)
