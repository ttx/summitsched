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

from django.conf.urls import patterns, url

from cheddar import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^(\d+)$', views.trackindex),
    url(r'^(\d+)/edit/(.+)$', views.modifysession),
    url(r'^(\d+)/swap/(.+)/(.+)$', views.swapsession),
    url(r'^(\d+)/(.+)$', views.editsession),
    url(r'^logout$', views.dologout),
    url(r'^loggedout$', views.loggedout),
)
