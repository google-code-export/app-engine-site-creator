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

"""Views for file browser."""


import models
import utility


def browser(request, page_id):
  """File Browser for built-in FCKeditor.

  Args:
    request: The request object
    page_id: ID of the page the files is attached to.

  Returns:
    A Django HttpResponse object.

  """

  page = None
  files = None
  files_type = request.GET.get('Type', None)

  if page_id:
    page = models.Page.get_by_id(int(page_id))

    if not page:
      return utility.page_not_found(request)

    if not page.user_can_write(request.profile):
      return utility.forbidden(request)

    files = page.attached_files()

    if files_type == 'Image':
      files = [item for item in files
               if item.name.lower().split('.')[-1] in utility.image_ext]

    if files_type == 'Flash':
      files = [item for item in files
               if item.name.lower().split('.')[-1] in utility.flash_ext]

    for item in files:
      icon = '/static/images/fileicons/%s.png' % item.name.lower().split('.')[-1]
      item.icon = icon

  return utility.respond(request, 'admin/filebrowser', {'files': files})
