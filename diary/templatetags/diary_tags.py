"""
Custom tags for use with the diary app.
"""
from django import template

register = template.Library()

@register.simple_tag
def update_variable(value):
    """
    Allows to update existing variable in template
    https://stackoverflow.com/questions/31916408/is-django-can-modify-variable-value-in-template
    """
    return value
