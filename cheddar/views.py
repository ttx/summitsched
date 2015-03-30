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

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.defaults import page_not_found
from django.conf import settings
from cheddar.sched import list_sessions, get_session, modify_session
from cheddar.session import session_to_form, form_to_session
from cheddar.tracklead import get_trackname, get_tracks, is_tracklead
from cheddar.tracklead import extra_tracks


def cheddar_render(request, template, **kwargs):
    kwargs['user'] = request.user
    kwargs['tracks'] = get_tracks(request.user.username)
    return render(request, template, kwargs)


@login_required
def index(request):
    tracks = get_tracks(request.user.username)
    if tracks:
        return trackindex(request, tracks[0].id)
    return cheddar_render(request, 'cheddar/notrack.html')


@login_required
@is_tracklead
def trackindex(request, trackid):
    return cheddar_render(request,
                          'cheddar/trackindex.html',
                          viewprefix="http://%s" % settings.SCHED_SITE,
                          trackname=get_trackname(trackid),
                          trackid=int(trackid),
                          session_list=list_sessions(trackid))


@login_required
@is_tracklead
def editsession(request, trackid, sessionkey):
    try:
        session = get_session(sessionkey)
    except IndexError:
        return page_not_found(request)
    return cheddar_render(
        request,
        'cheddar/editsession.html',
        viewprefix="http://%s" % settings.SCHED_SITE,
        trackname=get_trackname(trackid),
        trackid=int(trackid),
        extratracks=extra_tracks(int(trackid)),
        session=session_to_form(trackid, sessionkey, session))


def modifysession(request, trackid, sessionkey):
    session = form_to_session(trackid, sessionkey, request.POST)
    modify_session(sessionkey, session)
    return HttpResponseRedirect('/cheddar/%s' % trackid)


def loggedout(request):
    return cheddar_render(request, 'cheddar/loggedout.html')


def dologout(request):
    logout(request)
    return HttpResponseRedirect('/cheddar/loggedout')
