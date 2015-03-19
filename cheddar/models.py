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

from django.db import models


class Sched(models.Model):
    url = models.CharField(max_length=50, blank=True)
    api_key = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.url


class Track(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Tracklead(models.Model):
    track = models.ForeignKey(Track)
    user = models.CharField(max_length=40)

    def __unicode__(self):
        return "%s -> %s" % (self.user, self.track.name)
