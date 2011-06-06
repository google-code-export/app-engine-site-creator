#!/usr/bin/python2.5
#
# Copyright 2008 Google Inc.
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

"""Views for files management."""

import datetime
import logging
import mimetypes

from django import http
from django.core import validators
from django.core import exceptions
from google.appengine.ext import db

import models
import utility
import configuration


def upload_file(request):
  """Reads a file from POST data and stores it in the db.

  Args:
    request: The request object

  Returns:
    A http redirect to the edit form for the parent page

  """
  if not request.POST or not 'page_id' in request.POST:
    return utility.page_not_found(request)

  page_id = request.POST['page_id']
  page = models.Page.get_by_id(int(page_id))
  
  if not page:
    logging.warning('admin.upload_file was passed an invalid page id %r',
                    page_id)
    return utility.page_not_found(request)

  if not page.user_can_write(request.profile):
    return utility.forbidden(request)

  file_data = None
  file_name = None
  url = None
  if request.FILES and 'attachment' in request.FILES:
    file_name = request.FILES['attachment'].name
    file_data = request.FILES['attachment'].read()
  elif 'url' in request.POST:
    url = request.POST['url']
    file_name = url.split('/')[-1]
  else:
    return utility.page_not_found(request)

  if not url and not file_name:
    url = 'invalid URL'

  if url:
    validate = validators.URLValidator()
    try:
      validate(url)
    except exceptions.ValidationError, excption:
      return utility.page_not_found(request, excption.messages[0])

  file_record = page.get_attachment(file_name)

  if not file_record:
    file_record = models.FileStore(name=file_name, parent_page=page)

  if file_data:
    file_record.data = db.Blob(file_data)
  elif url:
    file_record.url = db.Link(url)

  # Determine whether to list the file when the page is viewed
  file_record.is_hidden = 'hidden' in request.POST

  file_record.put()
  utility.clear_memcache()

  return utility.edit_updated_page(page_id, tab_name='files')


def delete_file(request, page_id, file_id):
  """Removes a specified file from the database.

  Args:
    request: The request object
    page_id: ID of the page the file is attached to.
    file_id: Id of the file.

  Returns:
    A Django HttpResponse object.

  """
  record = models.FileStore.get_by_id(int(file_id))
  if record:
    if not record.user_can_write(request.profile):
      return utility.forbidden(request)

    record.delete()
    return utility.edit_updated_page(page_id, tab_name='files')
  else:
    return utility.page_not_found(request)


def send_file(file_record, request):
  """Sends a given file to a user if they have access rights.

  Args:
    file_record: The file to send to the user
    request: The Django request object

  Returns:
    A Django HttpResponse containing the requested file, or an error message.

  """
  profile = request.profile
  mimetype = mimetypes.guess_type(file_record.name)[0]

  if not file_record.user_can_read(profile):
    logging.warning('User %s made an invalid attempt to access file %s' %
                    (profile.email, file_record.name))
    return utility.forbidden(request)

  expires = datetime.datetime.now() + configuration.FILE_CACHE_TIME
  response = http.HttpResponse(content=file_record.data, mimetype=mimetype)
  response['Cache-Control'] = configuration.FILE_CACHE_CONTROL
  response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
  return response
