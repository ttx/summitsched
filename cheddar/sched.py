from django.conf import settings
import requests
from cheddar.models import Track

def call_sched(operation, **payload):
    schedsite = "http://%s/api" % settings.SCHED_SITE
    payload['api_key'] = settings.SCHED_API_KEY
    payload['format'] = "json"
    r = requests.post("%s/%s" % (schedsite, operation), params=payload)
    if r.text != u'Ok':
        return r.json()
    else:
        return {}

def list_sessions(trackid):
    t = Track.objects.get(id=trackid)
    unfiltered_list = call_sched('session/list')
    # TODO: this should use session prefix instead (to support
    # multiple event types)
    filtered = [a for a in unfiltered_list if a.get('event_type') == t.name]
    return sorted(filtered, key=lambda x: x['event_start'])

def get_session(sessionkey):
    unfiltered_list = call_sched('session/list')
    for session in unfiltered_list:
        if session['event_key'] == sessionkey:
            return session
    raise IndexError

def modify_session(sessionkey, session):
    # Sched clears "venue" information if you don't pass it again
    old_session = get_session(sessionkey)
    call_sched('session/mod',
               session_key=sessionkey,
               name=session['title'],
               description=session['description'],
               venue=old_session['venue'])
