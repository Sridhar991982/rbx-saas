from django.db.models.signals import post_save
from django.contrib.auth.models import User
from actstream import action
from rbx.models import UserProfile, Project


def on_user_profile_created(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(on_user_profile_created, sender=User)


def on_project_saved(sender, instance, created, **kwargs):
    verb = created and 'created' or 'updated'
    action.send(instance.owner.user, verb=verb, target=instance)

post_save.connect(on_project_saved, sender=Project)
