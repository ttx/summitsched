from cheddar.tracklead import get_trackname

WORKROOM_TITLE = "%s: Work session"
MEETUP_TITLE = "%s contributors meetup"
MEETUP_DESCRIPTION = "The %s contributors meetup is a informal gathering of the project contributors, with an open agenda.\n"
MEETUP_LINK = "\nClick <a href='%s'>here</a> for details on the meetup agenda."


def session_type(sessionkey):
    if sessionkey.startswith("slot-"):
        return 'FISHBOWL'
    if sessionkey.startswith("slot-"):
        return 'WORKROOM'
    return 'MEETUP'


def session_to_form(trackid, sessionkey, session):
    form = session.copy()
    form['description'] = form['description'].replace('<br />','\n')
    trackname = get_trackname(trackid)

    # Fishbowls keep their name, trackname is mandatory
    if form['sessiontype'] == 'FISHBOWL':
        if form['name'].startswith(trackname+": "):
            form['name'] = form['name'][len(trackname+": "):]
    # Workrooms & meetups have a mandatory name
    if form['sessiontype'] == 'WORKROOM':
        form['name'] = WORKROOM_TITLE % trackname
    if form['sessiontype'] == 'MEETUP':
        form['name'] = MEETUP_TITLE % trackname
        start = session['description'].find("<a href='")
        end = session['description'].find("here</a>")
        if start != -1 and end != -1:
            form['urllink'] = session['description'][start+9:end-2]
        else:
            form['urllink'] = ''

    return form


def form_to_session(trackid, sessionkey, formdata):

    session = formdata.copy()
    trackname = get_trackname(trackid)

    # Fishbowl can specify a name
    if session_type(sessionkey) == 'FISHBOWL':
        if not session['name'].startswith(trackname+": "):
            session['name'] = trackname+": "+ session['name']

    # Workrooms & meetups have a mandatory name and description
    if session_type(sessionkey) == 'WORKROOM':
        session['name'] = WORKROOM_TITLE % trackname

    if session_type(sessionkey) == 'MEETUP':
        session['name'] = MEETUP_TITLE % trackname
        session['description'] = MEETUP_DESCRIPTION % trackname
        if formdata['urllink']:
            session['description'] += MEETUP_LINK % formdata['urllink']

    session['description'] = session['description'].replace('\n','<br />')
    return session
