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
from cheddar.session import session_type

def call_sched(operation, **payload):
    schedsite = "http://%s/api" % settings.SCHED_SITE
    payload['api_key'] = settings.SCHED_API_KEY
    payload['format'] = "json"
    r = requests.post("%s/%s" % (schedsite, operation), params=payload)
    if r.text != u'Ok':
        return r.json()
    else:
        return {}

def all_sessions():
    complete_list = call_sched('session/list')
    for session in complete_list:
        session['sessiontype'] = session_type(session['event_key'])
    return complete_list

def list_sessions(trackid):
    t = Track.objects.get(id=trackid)
    # TODO: this should use session prefix instead (to support
    # multiple event types)
    filtered = [a for a in all_sessions() if a.get('event_type') == t.name]
    return sorted(filtered, key=lambda x: x['event_start'])

def get_session(sessionkey):
    for session in all_sessions():
        if session['event_key'] == sessionkey:
            return session
    raise IndexError

def modify_session(sessionkey, session):
    # Sched clears "venue" information if you don't pass it again
    old_session = get_session(sessionkey)
    call_sched('session/mod',
               session_key=sessionkey,
               name=session['name'],
               description=session['description'],
               venue=old_session['venue'])
