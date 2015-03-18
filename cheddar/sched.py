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
