import os
from json import loads
from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from settings import EDIT_RIGHT, ADMIN_RIGHT, STORAGE

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
def can_admin(project, user):
    return project.is_allowed(user, ADMIN_RIGHT)


@register.filter
def profile_url(user, username):
    return mark_safe('<a href="%s">%s</a>' %
                     (reverse('profile', args=[username]), user))


@register.filter
def error_block(msg):
    return mark_safe('<span class="help-block">%s</span>' % msg)


@register.filter
def elapsed(seconds):
    suffixes = ['y', 'w', 'd', 'h', 'm', 's']
    add_s = False
    separator = ' '
    time = []
    parts = [(suffixes[0], 60 * 60 * 24 * 7 * 52),
             (suffixes[1], 60 * 60 * 24 * 7),
             (suffixes[2], 60 * 60 * 24),
             (suffixes[3], 60 * 60),
             (suffixes[4], 60),
             (suffixes[5], 1)]
    if seconds == 0:
        return str(seconds) + suffixes[-1]
    for suffix, length in parts:
        value = int(seconds / length)
        if value > 0:
            seconds = seconds % length
            time.append('%s%s' % (str(value),
                                  (suffix, (suffix, suffix + 's')[value > 1])[add_s]))
            if seconds < 1:
                break
    return separator.join(time)


@register.filter
def own_run(runs, user):
    if not user.is_authenticated():
        return []
    return [r for r in runs if r.user == user.get_profile()]


@register.filter
def restrict(projects, user):
    if not user.is_authenticated():
        return [p for p in projects if p.public]
    return [p for p in projects if p.public or p.is_allowed(user)]


@register.filter
def hide(obj, user):
    return [o for o in obj if not hasattr(o.object, 'is_allowed') or o.object.is_allowed(user)]


@register.filter
def from_json(struct, field):
    json = loads(struct)
    return json.get(field, '')


@register.filter
def basename(filename):
    return os.path.basename(filename)


@register.filter
def is_image(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ('.gif', '.jpeg', '.jpg', '.png')


@register.filter
def is_text(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ('', '.md', '.markdown', '.txt', '.log',
                           '.properties', '.rst', '.c', '.cpp', '.xml', '.err')


@register.filter
def get_content(filename):
    with open(os.path.join(STORAGE, filename)) as fd:
        return fd.read()
