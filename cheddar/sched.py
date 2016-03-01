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

import requests
from cheddar.models import Track
from cheddar.session import Session
from cheddar.tracklead import is_valid_track


class API:

    def __init__(self, settings):
        self.schedurl = "http://%s/api" % settings.SCHED_SITE
        self.api_key = settings.SCHED_API_KEY

    def _call_sched(self, operation, **payload):
        payload['api_key'] = self.api_key
        payload['format'] = "json"
        r = requests.post("%s/%s" % (self.schedurl, operation), params=payload)
        if r.text != u'Ok':
            return r.json()
        else:
            return {}

    def _sched_to_session(self, schedjson):
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

        session.extratracks = schedjson['event_type'].replace(
            session.maintrack,"")
        session.extratracks = session.extratracks.strip(" ,")

        session.set_title(schedjson['name'])
        try:
            session.set_desc(schedjson['description'])
        except KeyError:
            session.description = "tbd"

        return session

    def _all_sessions(self):
        ret = self._call_sched('session/list')
        sessions = []
        for sessionjson in ret:
            sessions.append(self._sched_to_session(sessionjson))
        return sessions


    def list_sessions(self, trackid):
        t = Track.objects.get(id=trackid)
        def track_match(a):
            return a.maintrack == t.name
        filtered = filter(track_match, self._all_sessions())
        return sorted(filtered, key=lambda x: x.start)


    def get_session(self, sessionkey):
        for session in self._all_sessions():
            if session.id == sessionkey:
                return session
        raise IndexError


    def modify_session(self, sessionkey, session):
        # Sched clears "venue" information if you don't pass it again
        old_session = self.get_session(sessionkey)
        alltracks = session.maintrack
        description = session.description
        for track in session.extratracks.split(","):
            track = track.strip().capitalize()
            if is_valid_track(track):
                print track
                alltracks = "%s, %s" % (alltracks, track)

        name = session.get_title()
        description = session.get_desc()

        self._call_sched('session/mod',
                         session_key=sessionkey,
                         name=name,
                         session_type=alltracks,
                         description=description,
                         venue=old_session.room)


    def create_session(self, index, day, starttime, endtime, title,
                       desc, track, room, style):
        key = "%s-%s-%d" % (style.lower().capitalize()[0:4], track, index)
        self._call_sched('session/add',
                         session_key=key,
                         name=title,
                         session_start=day + " " + starttime,
                         session_end=day + " " + endtime,
                         session_type=track,
                         description=desc,
                         venue=room)
