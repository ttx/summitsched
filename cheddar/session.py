from cheddar.tracklead import get_trackname

WORKROOM_TITLE = "%s: Work session"
MEETUP_TITLE = "%s contributors meetup"


def session_type(sessionkey):
    if sessionkey.startswith("slot-"):
        return 'FISHBOWL'
    if sessionkey.startswith("slot-"):
        return 'WORKROOM'
    if sessionkey.startswith("slot-"):
        return 'MEETUP'


def session_to_form(trackid, sessionkey, session):
    form = session.copy()
    form['description'] = form['description'].replace('<br />','\n')
    trackname = get_trackname(trackid)
    form['sessiontype'] = session_type(sessionkey)

    # Fishbowls keep their name, trackname is mandatory
    if form['sessiontype'] == 'FISHBOWL':
        if form['name'].startswith(trackname+": "):
            form['name'] = form['name'][len(trackname+": "):]
    # Workrooms & meetups have a mandatory name
    if form['sessiontype'] == 'WORKROOM':
        form['name'] = WORKROOM_TITLE % trackname
    if form['sessiontype'] == 'MEETUP':
        form['name'] = MEETUP_TITLE % trackname

    return form


def form_to_session(trackid, sessionkey, formdata):

    session = formdata.copy()
    session['description'] = session['description'].replace('\n','<br />')
    trackname = get_trackname(trackid)

    # Fishbowl can specify a name
    if session_type(sessionkey) == 'FISHBOWL':
        if not session['name'].startswith(trackname+": "):
            session['name'] = trackname+": "+ session['name']
    # Workrooms & meetups have a mandatory name
    if session_type(sessionkey) == 'WORKROOM':
        session['name'] = WORKROOM_TITLE % trackname
    if session_type(sessionkey) == 'MEETUP':
        session['name'] = MEETUP_TITLE % trackname

    return session
