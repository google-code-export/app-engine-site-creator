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

"""Views for thr Blobstore management."""

import cgi
import datetime
import logging

from django import http
from django.core import validators
from django.core import exceptions
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images

import models
import utility
import configuration


def upload_blob(request):
  """Reads a file from POST data and stores it in the Blobstore.

  Args:
    request: The request object

  Returns:
    A http redirect to the edit form for the parent page

  """

  fields = cgi.FieldStorage()

  if not fields.has_key('page_id'):
    return utility.edit_updated_page(tab_name='files')

  page_id = fields['page_id'].value
  page = models.Page.get_by_id(int(page_id))
  
  if not page:
    logging.warning('blobs.upload_file was passed an invalid page id %r',
                    page_id)
    return utility.edit_updated_page(page_id, tab_name='files')

  if not page.user_can_write(request.profile):
    return utility.edit_updated_page(page_id, tab_name='files')

  blob_info = None
  file_name = None
  url = None
  if fields.has_key('attachment'):
    file_field = fields['attachment']
    blob_info = blobstore.parse_blob_info(file_field)
    file_name = blob_info.filename
  elif 'url' in fields:
    url = fields['url'].value
    file_name = url.split('/')[-1]
  else:
    return utility.edit_updated_page(page_id, tab_name='files')

  if not url and not file_name:
    url = 'invalid URL'

  if url:
    validate = validators.URLValidator()
    try:
      validate(url)
    except exceptions.ValidationError:
      return utility.edit_updated_page(page_id, tab_name='files')

  file_record = page.get_attachment(file_name)

  if not file_record:
    file_record = models.BlobStore(name=file_name, parent_page=page)

  if blob_info:
    file_record.blob_key = blob_info.key()
  elif url:
    file_record.url = db.Link(url)

  # Determine whether to list the file when the page is viewed
  file_record.is_hidden = 'hidden' in fields

  file_record.put()
  utility.clear_memcache()

  return utility.edit_updated_page(page_id, tab_name='files')


def delete_blob(request, page_id, file_id):
  """Removes a specified file from the Blobstore.

  Args:
    request: The request object
    page_id: ID of the page the file is attached to.
    file_id: Id of the file.

  Returns:
    A Django HttpResponse object.

  """
  record = models.BlobStore.get_by_id(int(file_id))
  if record:
    if not record.user_can_write(request.profile):
      return utility.forbidden(request)

    record.delete()
    return utility.edit_updated_page(page_id, tab_name='files')
  else:
    return utility.page_not_found(request)


def send_blob(file_record, request):
  """Sends a given file to a user if they have access rights.
     Images can be transformed if GET parameter has been added to the URL:
     - s=<value in pixels> - for resize image
     - c=<value in pixels> - for crop image

  Args:
    file_record: The file to send to the user
    request: The Django request object

  Returns:
    A Django HttpResponse containing the requested file, or an error message.

  """
  profile = request.profile
  content = None
  mimetype = file_record.blob_data.content_type
  file_ext = file_record.name.lower().split('.')[-1]

  if not file_record.user_can_read(profile):
    logging.warning('User %s made an invalid attempt to access file %s' %
                    (profile.email, file_record.name))
    return utility.forbidden(request)

  if request.GET.get('s') and file_ext in utility.image_ext:
    if not request.GET.get('s').isdigit():
      return utility.page_not_found(request)
    s = int(request.GET.get('s'))
    img = images.Image(blob_key=file_record.blob_key)
    img.resize(width=s, height=s)
    thumb = img.execute_transforms() # needed to run before you get the metadata
    metadata = img.get_original_metadata()
    if metadata['ImageWidth'] > s and metadata['ImageLength'] > s:
      content = thumb
      mimetype = 'image/png'
  elif request.GET.get('c') and file_ext in utility.image_ext:
    if not request.GET.get('c').isdigit():
      return utility.page_not_found(request)
    c = int(request.GET.get('c'))
    img = images.Image(blob_key=file_record.blob_key)
    img.resize(width=c, height=c)
    img.execute_transforms() # needed to run before you get the metadata
    metadata = img.get_original_metadata()
    width, height = metadata['ImageWidth'], metadata['ImageLength']
    if width > height:
      x = (width-height)/float(width*2)
      img.crop(x, 0.0, 1-x, 1.0)
    if width < height:
      y = (height-width)/float(height*2)
      img.crop(0.0, y, 1.0, 1-y)
    img.resize(width=c, height=c)
    content = img.execute_transforms()
    mimetype = 'image/png'

  response = http.HttpResponse(mimetype=mimetype)

  if content:
    response.write(content)
  else:
    response[blobstore.BLOB_KEY_HEADER] = file_record.blob_key

  if not file_ext in utility.image_ext + utility.flash_ext:
    response['Content-Disposition'] = ('attachment; filename=%s' %
                                        file_record.name)

  expires = datetime.datetime.now() + configuration.FILE_CACHE_TIME
  response['Cache-Control'] = configuration.FILE_CACHE_CONTROL
  response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
  return response
