import requests
from cheddar.models import Track

def call_sched(operation, **payload):
    schedsite = "http://kilodesignsummit.sched.org/api"
    payload['api_key'] = "c1a3f10f367a3a418573fc8a10b7cdf5"
    payload['format'] = "json"
    r = requests.get("%s/%s" % (schedsite, operation), params=payload)
    return r.json()

def list_sessions(trackid):
    t = Track.objects.get(id=trackid)
    unfiltered_list = call_sched('session/list')
    # TODO: this should use session prefix instead (to support
    # multiple event types)
    filtered = [a for a in unfiltered_list if a.get('event_type') == t.name]
    return sorted(filtered, key=lambda x: x['event_start'])
