from django import template

register = template.Library()


@register.filter(name="kebab")
def kebab(value):
    return value.replace(" ", "-")
