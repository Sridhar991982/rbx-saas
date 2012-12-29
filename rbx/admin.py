from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rbx.models import UserProfile, Project, ProjectRight, \
    ProjectField, Executor, ExecutorParam, Build, BuildParam


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project)
admin.site.register(ProjectRight)
admin.site.register(ProjectField)
admin.site.register(Executor)
admin.site.register(ExecutorParam)
admin.site.register(Build)
admin.site.register(BuildParam)
