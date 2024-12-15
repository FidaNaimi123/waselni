# myapp/templatetags/form_filters.py

from django import template
import base64

register = template.Library()

@register.filter
def add_class(value, arg):
    return value.as_widget(attrs={"class": arg})

@register.filter
def b64encode(value):
    return base64.b64encode(value.encode()).decode()
