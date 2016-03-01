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
        self.summit_type_id = settings.SUM_SUMMITTYPEID
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
        # Using a custom ofset since the one stored in Summit looks incorrect
        self.timezone_offset = settings.SUM_TZOFFSET


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
            time = datetime.datetime.utcfromtimestamp(
                timestamp + self.timezone_offset)
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
            tagname = tag['tag'].capitalize()
            if tagname != session.maintrack:
                session.extratracks = session.extratracks + tagname + ", "
        session.extratracks = session.extratracks.strip(" ,")

        session.set_title(sjson['title'])
        session.set_desc(sjson['description'])

        return session


    def list_sessions(self, trackid):
        t = Track.objects.get(id=trackid)
        ret = self._call_summit('get','events', debug=True, payload={
            'page': 1,
            'per_page': 100,
            'filter': [ 'summit_type_id==%d' % self.summit_type_id,
                'tags=@%s' % t.name ]
             })
        sessions = []
        for sessionjson in sorted(ret['data'],
                                  key=lambda x: x['start_date']):
            if sessionjson['title'].startswith(t.name + ": "):
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

        name = session.get_title()
        description = session.get_desc()

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
            "summit_types_id":[ self.summit_type_id ],
            "tags": [ track ],
            "type_id": self.eventids[style] })
