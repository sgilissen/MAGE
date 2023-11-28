from django import template
from django.templatetags.static import PrefixNode
from django.contrib.staticfiles.finders import find

register = template.Library()


@register.filter(name='file_exists')
def file_exists(value):
    return find(value) is not None
