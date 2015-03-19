# Copyright 2015 Thierry Carrez <thierry@openstack.org>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cheddar.models import Track, Tracklead
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def get_trackname(trackid):
    track = get_object_or_404(Track, id=trackid)
    return track.name


def get_tracks(leadname):
    trackleads = Tracklead.objects.filter(user=leadname)
    return [t.track for t in trackleads]


def is_tracklead(func):
    def wrapper(*args, **kwargs):
        track = get_object_or_404(Track, id=args[1])
        if track not in get_tracks(args[0].user.username):
            raise PermissionDenied
        return func(*args, **kwargs)
    return wrapper
