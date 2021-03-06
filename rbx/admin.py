from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rbx.models import UserProfile, Project, ProjectRight, \
    Box, BoxParam, Run, RunParam, Invitation, System, Software, \
    SoftwareCategory, SoftwareInstallation


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


class ProjectRightInline(admin.TabularInline):
    model = ProjectRight


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    inlines = (ProjectRightInline,)
    prepopulated_fields = {'slug': ('name',)}


class BoxParamInline(admin.TabularInline):
    model = BoxParam


class BoxAdmin(admin.ModelAdmin):
    model = Box
    inlines = (BoxParamInline,)


class RunParamInline(admin.TabularInline):
    model = RunParam


class RunAdmin(admin.ModelAdmin):
    model = Run
    inlines = (RunParamInline,)
    list_filter = ('started',)


class InvitationAdmin(admin.ModelAdmin):
    list_filter = ('request_date',)
    list_display = ('email', 'request_date')


class SoftwareParamInline(admin.TabularInline):
    model = Software


class SystemAdmin(admin.ModelAdmin):
    model = System
    inlines = (SoftwareParamInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Box, BoxAdmin)
admin.site.register(Run, RunAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(System, SystemAdmin)
admin.site.register(SoftwareCategory)
admin.site.register(SoftwareInstallation)
