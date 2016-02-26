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

class Session():

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

    def __init__(self, sessionid):
        self.id = sessionid

    def modify_using_formdata(self, formdata):
        self.extratracks = formdata['extratracks']
        self.title = formdata.get('title')
        self.urllink = formdata.get('urllink')
        self.description = formdata['description']

