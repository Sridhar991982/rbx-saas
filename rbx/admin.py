from django.contrib import admin
from rbx.models import UserProfile, Project, ProjectRight, \
    ProjectField, Executor, ExecutorParam, Build, BuildParam

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(ProjectRight)
admin.site.register(ProjectField)
admin.site.register(Executor)
admin.site.register(ExecutorParam)
admin.site.register(Build)
admin.site.register(BuildParam)
