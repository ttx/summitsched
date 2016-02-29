# Copyright 2016 Thierry Carrez <thierry@openstack.org>
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

import datetime
import json
import requests
from cheddar.models import Track
from cheddar.session import Session
from cheddar.tracklead import is_valid_track

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class API:

    def __init__(self, settings):
        requests.packages.urllib3.disable_warnings()
        basescope = settings.SUM_RESOURCESRV + '/summits/'
        self.scopes = [ basescope + 'read',
           basescope + 'write-event',
           basescope + 'publish-event',
           basescope + 'delete-event' ]
        self.endpoint = ( settings.SUM_RESOURCESRV +
                          '/api/v1/summits/' +
                          settings.SUM_SUMMITID + '/' )
        self.clientid = settings.SUM_CLIENTID
        self.oauth = OAuth2Session(
            client=BackendApplicationClient(client_id=self.clientid))
        self.token = self.oauth.fetch_token(
            token_url=settings.SUM_TOKENURL,
            client_id=self.clientid,
            client_secret=settings.SUM_SECRET,
            verify=False,
            scope=self.scopes)
        self.eventids = settings.SUM_EVENTIDS


    def _call_summit(self, method, call, payload=None, debug=False):
        if debug:
            print method, self.endpoint, call
            if payload:
                print json.dumps(payload,
                         sort_keys=True, indent=4, separators=(',', ': '))
            print "--->"

        r = self.oauth.request(method, self.endpoint + call,
                               verify=False, json=payload)

        try:
            if debug:
                print str(r.status_code)
                if r.text:
                    print json.dumps(r.json(),
                         sort_keys=True, indent=4, separators=(',', ': '))
                print "==================================="
            return r.json()
        except ValueError:
            return {}


    def _summit_to_session(self, sjson):
        session = Session(sjson['id'])

        def _format_datetime(timestamp):
            time = datetime.datetime.utcfromtimestamp(timestamp)
            return time.strftime('%Y-%m-%d %H:%M:%S')

        session.start = _format_datetime(sjson['start_date'])
        session.end = _format_datetime(sjson['end_date'])
        session.room = sjson['location_id']

        session.style = 'FISHBOWL' # FIXME sjson['class_name']

        elements = sjson['title'].split(":")
        if len(elements) < 1:
            session.maintrack = ""
        else:
            session.maintrack = elements[0]

        session.extratracks = ""
        for tag in sjson['tags']:
            if tag['tag'] != session.maintrack:
                session.extratracks = session.extratracks + tag['tag'] + ", "
        session.extratracks = session.extratracks.strip(" ,")

        # Fishbowls keep their name, trackname is mandatory
        if session.style == 'FISHBOWL':
            if sjson['title'].startswith(session.maintrack+": "):
                session.title = sjson['title'][len(session.maintrack+": "):]
            else:
                session.title = sjson['title']

        # Workrooms & meetups have a mandatory name
        if session.style == 'WORKROOM':
            session.title = Session.WORKROOM_TITLE % session.maintrack

        if session.style == 'MEETUP':
            session.title = Session.MEETUP_TITLE % session.maintrack

        session.description = sjson['description']

        start = sjson['description'].find("<a href='")
        end = sjson['description'].find("here</a>")
        if start != -1 and end != -1:
            session.urllink = sjson['description'][start+9:end-2]
        else:
            session.urllink = ''

        return session


    def list_sessions(self, trackid):
        t = Track.objects.get(id=trackid)
        ret = self._call_summit('get','events',
                                payload={ 'per_page': 100,
                                  'filter': 'tags=@'+t.name,
                                }, debug=True)
        sessions = []
        for sessionjson in sorted(ret['data'],
                                  key=lambda x: x['start_date']):
            sessions.append(self._summit_to_session(sessionjson))

        return sessions


    def get_session(self, sessionid):
        ret = self._call_summit('get','events/'+str(sessionid))
        return self._summit_to_session(ret)


    def modify_session(self, sessionkey, session):
        alltracks = [ session.maintrack ]
        description = session.description
        for track in session.extratracks.split(","):
            track = track.strip().capitalize()
            if is_valid_track(track):
                alltracks.append(track)

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

        self._call_summit('put', 'events/%s' % sessionkey, payload={
                         'title': name,
                         'tags': alltracks,
                         'description': description})


    def create_session(self, key, day, starttime, endtime, title,
                       desc, track, room, style):
        def _dt_to_timestamp(ds):
            dt = datetime.datetime.strptime(ds, "%Y-%m-%d %H:%M")
            return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())

        self._call_summit('post', 'events', payload={
            "title": title,
            "start_date": _dt_to_timestamp(day + " " + starttime),
            "end_date": _dt_to_timestamp(day + " " + endtime),
            "description": desc,
            "location_id": int(room), # FIXME
            "summit_types_id":[2],
            "tags": [ track ],
            "type_id": self.eventids[style] })