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

"""Main view for sitemap."""

from django import http
from django.template import loader
from django.core import urlresolvers
from django.utils.encoding import smart_str
import models


def sitemap(request):
  """Generates sitemap.xml file for pages that have global access.

  Args:
    request: The Django request object

  Returns:
    A Django HttpResponse object containing the file data.

  """

  urls = []

  for page in models.Page.all():
    global_access = page.acl.global_read
    if not global_access:
      continue
    url = urlresolvers.reverse('views.main.get_url', args=[page.path])
    url = request.build_absolute_uri(url)
    lastmod = page.modified
    urls.append([url, lastmod])

  xml = smart_str(loader.render_to_string('sitemap.xml', {'urlset': urls}))
  return http.HttpResponse(xml, mimetype='application/xml')
