from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def get_item(obj, key):
    try:
        return obj[key]
    except (KeyError, IndexError, TypeError):
        return ''
