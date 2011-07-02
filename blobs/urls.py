#!/usr/bin/python2.5
#
# Copyright 2011 App Engine Site Creator
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Defines the url patterns for the application."""

# pylint: disable-msg=C0103,C0301

from django.conf.urls import defaults

urlpatterns = defaults.patterns(
    'blobs.views',
    (r'add/$', 'upload_blob'),
    defaults.url(r'delete/([\w\-]+)/([^\s/]+)$',
                  'delete_blob', name='blob-delete'),
)
