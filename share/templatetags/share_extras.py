from django import template
from django.utils.safestring import mark_safe
from share.enums import MEMBER_ROLE_MAP

register = template.Library()

@register.filter
def get_member_role_ch(value):
    return MEMBER_ROLE_MAP.get(value, '')