from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def split_tracks(value):
    extra = []
    tracks = value.split(",")
    for track in tracks:
        extra.append(track.strip())
    return extra
