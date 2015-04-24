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

from cheddar.tracklead import get_trackname, is_valid_track

WORKROOM_TITLE = "%s: Work session"
WORKROOM_DESCRIPTION = (
    "Work sessions are for %s contributors to discuss implementation details "
    "and making quick progress over specific issues, "
    "in a small work group environment.\n")
WORKROOM_LINK = (
    "\nClick <a href='%s'>here</a> for details on this work room agenda.")

MEETUP_TITLE = "%s contributors meetup"
MEETUP_DESCRIPTION = (
    "The %s contributors meetup is a informal gathering of "
    "the project contributors, with an open agenda.\n")
MEETUP_LINK = (
    "\nClick <a href='%s'>here</a> for details on the meetup agenda.")


def session_type(sessionkey):
    if sessionkey.startswith("Fish-"):
        return 'FISHBOWL'
    if sessionkey.startswith("Meet-"):
        return 'MEETUP'
    return 'WORKROOM'


def session_track(sessionkey):
    elements = sessionkey.split("-")
    if len(elements) < 2:
        return ""
    return elements[1]


def session_to_form(trackid, sessionkey, session):
    form = session.copy()

    try:
        form['description'] = form['description'].replace('<br />', '\n')
    except KeyError:
        form['description'] = "tbd"

    trackname = get_trackname(trackid)

    form['event_subtype'] = form['event_subtype'].replace(trackname,"")
    form['event_subtype'] = form['event_subtype'].strip(" ,")

    # Fishbowls keep their name, trackname is mandatory
    if form['sessiontype'] == 'FISHBOWL':
        if form['name'].startswith(trackname+": "):
            form['name'] = form['name'][len(trackname+": "):]
    else:
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

    session['tracks'] = trackname
    for track in formdata['tracks'].split(","):
        track = track.strip().capitalize()
        if is_valid_track(track):
            session['tracks'] = "%s, %s" % (session['tracks'], track)

    # Fishbowl can specify a name
    if session_type(sessionkey) == 'FISHBOWL':
        if not session['name'].startswith(trackname+": "):
            session['name'] = trackname + ": " + session['name']

    # Workrooms have a mandatory name
    if session_type(sessionkey) == 'WORKROOM':
        session['name'] = WORKROOM_TITLE % trackname

    # Meetups have a mandatory name and description
    if session_type(sessionkey) == 'MEETUP':
        session['name'] = MEETUP_TITLE % trackname
        session['description'] = MEETUP_DESCRIPTION % trackname
        if formdata['urllink']:
            session['description'] += MEETUP_LINK % formdata['urllink']

    session['description'] = session['description'].replace('\n', '<br />')
    return session
