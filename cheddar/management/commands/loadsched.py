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

import json
import datetime

from django.core.management.base import BaseCommand, CommandError
from cheddar.models import Track, Tracklead
from cheddar.session import Session
from cheddar.api import load_api


def _endtime(start_time, duration):
    start = datetime.datetime.strptime(start_time, "%H:%M")
    end = start + datetime.timedelta(minutes=duration)
    return end.strftime("%H:%M")


class Command(BaseCommand):
    args = '<description.json>'
    help = 'Create topics from JSON description'

    def handle(self, *args, **options):

        if len(args) != 1:
            raise CommandError('Incorrect arguments')

        try:
            with open(args[0]) as f:
                data = json.load(f)
        except ValueError as exc:
            raise CommandError("Malformed JSON: %s" % exc.message)

        api = load_api()

        for track, leads in data['tracks'].iteritems():
            t = Track(name=track)
            t.save()
            for lead in leads:
                l = Tracklead(track=t, user=lead)
                l.save()

        index = 0
        for room in data['rooms']:
            for day, slots in room['days'].iteritems():
                for slot in slots:
                    if not slot['track']:
                        continue
                    index = index + 1
                    if room['style'] == 'FISHBOWL':
                        duration = 40
                        title = "%s: tbd" % slot['track']
                        desc = "tbd"
                    if room['style'] == 'WORKROOM':
                        duration = 40
                        title = Session.WORKROOM_TITLE % slot['track']
                        desc = Session.WORKROOM_DESCRIPTION % slot['track']
                    if room['style'] == 'MEETUP':
                        duration = 210
                        title = Session.MEETUP_TITLE % slot['track']
                        desc = Session.MEETUP_DESCRIPTION % slot['track']
                    api.create_session(
                        index,
                        day,
                        slot['time'],
                        _endtime(slot['time'], duration),
                        title,
                        desc,
                        slot['track'],
                        room['name'],
                        room['style']
                    )
