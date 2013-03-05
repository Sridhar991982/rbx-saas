from datetime import datetime
from haystack import indexes
from haystack import site
from rbx.models import UserProfile, Project


class UserProfileIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def index_queryset(self):
        return UserProfile.objects.filter(user__date_joined__lte=datetime.now())

site.register(UserProfile, UserProfileIndex)


class ProjectIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    owner = indexes.CharField(model_attr='owner')
    created = indexes.DateTimeField(model_attr='created')
    updated = indexes.DateTimeField(model_attr='updated')
    description = indexes.CharField(model_attr='description')

    def index_queryset(self):
        return Project.objects.filter(created__lte=datetime.now())

site.register(Project, ProjectIndex)
