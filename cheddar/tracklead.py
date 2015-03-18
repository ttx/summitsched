from cheddar.models import Track, Tracklead
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

def get_trackname(trackid):
    track = get_object_or_404(Track, id=trackid)
    return track.name

def get_tracks(leadname):
    trackleads = Tracklead.objects.filter(user=leadname)
    return [ t.track for t in trackleads ]


def is_tracklead(func):
    def wrapper(*args, **kwargs):
        track = get_object_or_404(Track, id=args[1])
        if track not in get_tracks(args[0].user.username):
             raise PermissionDenied
        return func(*args, **kwargs)
    return wrapper
