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

from django.conf import settings
import requests
from cheddar.models import Track
from cheddar.session import Session
from cheddar.tracklead import is_valid_track


def _call_sched(operation, **payload):
    schedsite = "http://%s/api" % settings.SCHED_SITE
    payload['api_key'] = settings.SCHED_API_KEY
    payload['format'] = "json"
    r = requests.post("%s/%s" % (schedsite, operation), params=payload)
    if r.text != u'Ok':
        return r.json()
    else:
        return {}


def _sched_to_session(schedjson):
    session = Session(schedjson['event_key'])
    session.start = schedjson['event_start']
    session.end = schedjson['event_end']
    session.room = schedjson['venue']

    session.style = 'WORKROOM'
    if session.id.startswith("Fish-"):
        session.style = 'FISHBOWL'
    if session.id.startswith("Meet-"):
        session.style = 'MEETUP'

    elements = session.id.split("-")
    if len(elements) < 2:
        session.maintrack = ""
    else:
        session.maintrack = elements[1]

    session.extratracks = schedjson['event_type'].replace(session.maintrack,"")
    session.extratracks = session.extratracks.strip(" ,")

    # Fishbowls keep their name, trackname is mandatory
    if session.style == 'FISHBOWL':
        if schedjson['name'].startswith(session.maintrack+": "):
            session.title = schedjson['name'][len(session.maintrack+": "):]
        else:
            session.title = schedjson['name']

    # Workrooms & meetups have a mandatory name
    if session.style == 'WORKROOM':
        session.title = Session.WORKROOM_TITLE % session.maintrack

    if session.style == 'MEETUP':
        session.title = Session.MEETUP_TITLE % session.maintrack

    try:
        session.description = schedjson['description'].replace('<br />', '\n')
    except KeyError:
        session.description = "tbd"

    start = schedjson['description'].find("<a href='")
    end = schedjson['description'].find("here</a>")
    if start != -1 and end != -1:
        session.urllink = schedjson['description'][start+9:end-2]
    else:
        session.urllink = ''

    return session


def _all_sessions():
    ret = _call_sched('session/list')
    sessions = []
    for sessionjson in ret:
        sessions.append(_sched_to_session(sessionjson))
    return sessions


def list_sessions(trackid):
    t = Track.objects.get(id=trackid)
    def track_match(a):
        return a.maintrack == t.name
    filtered = filter(track_match, _all_sessions())
    return sorted(filtered, key=lambda x: x.start)


def get_session(sessionkey):
    for session in _all_sessions():
        if session.id == sessionkey:
            return session
    raise IndexError


def modify_session(sessionkey, session):
    # Sched clears "venue" information if you don't pass it again
    old_session = get_session(sessionkey)
    alltracks = session.maintrack
    description = session.description
    for track in session.extratracks.split(","):
        track = track.strip().capitalize()
        if is_valid_track(track):
            print track
            alltracks = "%s, %s" % (alltracks, track)

    # Fishbowl can specify a name
    if session.style == 'FISHBOWL':
        if not session.title.startswith(session.maintrack+": "):
            name = session.maintrack + ": " + session.title
        else:
            name = session.title

    # Workrooms have a mandatory name
    if session.style == 'WORKROOM':
        name = Session.WORKROOM_TITLE % session.maintrack

    # Meetups have a mandatory name and description
    if session.style == 'MEETUP':
        name = Session.MEETUP_TITLE % session.maintrack
        description = Session.MEETUP_DESCRIPTION % session.maintrack
        if session.urllink:
            description += Session.MEETUP_LINK % session.urllink

    description = description.replace('\n', '<br />')

    _call_sched('session/mod',
               session_key=sessionkey,
               name=name,
               session_type=alltracks,
               description=description,
               venue=old_session.room)


def create_session(key, day, starttime, endtime, title, desc, track, room):
    _call_sched('session/add',
               session_key=key,
               name=title,
               session_start=day + " " + starttime,
               session_end=day + " " + endtime,
               session_type=track,
               description=desc,
               venue=room)
