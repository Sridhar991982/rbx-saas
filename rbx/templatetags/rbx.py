from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from settings import EDIT_RIGHT

register = template.Library()


@register.simple_tag
def title(value):
    return '%s &mdash; Run in the Box' % value


@register.filter
def is_visible(project, user):
    return project.is_allowed(user)


@register.filter
def is_editable(project, user):
    return project.is_allowed(user, EDIT_RIGHT)


@register.filter
def profile_url(user, username):
    return mark_safe('<a href="%s">%s</a>' % (reverse('profile',
                                            args=[username]), user))


@register.filter
def error_block(msg):
    return mark_safe('<span class="help-block">%s</span>' % msg)
