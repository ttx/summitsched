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
from cheddar.api import load_api
from cheddar.tracklead import get_trackname, get_tracks, is_tracklead
from cheddar.tracklead import extra_tracks


api = load_api()

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
    trackname = get_trackname(trackid)
    linkurl = settings.TRACKLINK % trackname
    return cheddar_render(request,
                          'cheddar/trackindex.html',
                          linkurl=linkurl,
                          trackname=trackname,
                          trackid=int(trackid),
                          session_list=api.list_sessions(trackid))


@login_required
@is_tracklead
def editsession(request, trackid, sessionkey):
    try:
        session = api.get_session(sessionkey)
    except IndexError:
        return page_not_found(request)
    linkurl = settings.SESSIONLINK % sessionkey
    return cheddar_render(
        request,
        'cheddar/editsession.html',
        linkurl=linkurl,
        trackname=get_trackname(trackid),
        trackid=int(trackid),
        extratracks=extra_tracks(int(trackid)),
        session=session)


@login_required
@is_tracklead
def modifysession(request, trackid, sessionkey):
    session = api.get_session(sessionkey)
    session.modify_using_formdata(request.POST)
    api.modify_session(sessionkey, session)
    return HttpResponseRedirect('/cheddar/%s' % trackid)


@login_required
@is_tracklead
def swapsession(request, trackid, sessionkey, session2key):
    session = api.get_session(sessionkey)
    session2 = api.get_session(session2key)
    api.swap_sessions(sessionkey, session, session2key, session2)
    return HttpResponseRedirect('/cheddar/%s' % trackid)


def loggedout(request):
    return cheddar_render(request, 'cheddar/loggedout.html')


def dologout(request):
    logout(request)
    return HttpResponseRedirect('/cheddar/loggedout')
