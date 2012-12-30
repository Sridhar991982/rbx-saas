from django import template

register = template.Library()


@register.simple_tag
def title(value):
    return '%s &mdash; Run in the Box' % value
