from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.defaults import page_not_found
from cheddar.sched import list_sessions, get_session, modify_session
from cheddar.session import session_to_form, form_to_session
from cheddar.tracklead import get_trackname, get_tracks, is_tracklead


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
    return cheddar_render(request,
                          'cheddar/editsession.html',
                          trackname=get_trackname(trackid),
                          trackid=int(trackid),
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
