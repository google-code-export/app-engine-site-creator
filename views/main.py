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

"""Main views for viewing pages and downloading files."""

import datetime
import logging

import configuration
from django import http
from django.core import urlresolvers
from django.utils import simplejson
from google.appengine.api import images
import models
import utility


def send_page(page, request):
  """Sends a given page to a user if they have access rights.

  Args:
    page: The page to send to the user
    request: The Django request object

  Returns:
    A Django HttpResponse containing the requested page, or an error message.

  """
  profile = request.profile
  global_access = page.acl.global_read
  if not global_access:
    if profile is None:
      return http.HttpResponseRedirect(users.create_login_url(request.path))
    if not page.user_can_read(profile):
      logging.warning('User %s made an invalid attempt to access page %s' %
                      (profile.email, page.name))
      return utility.forbidden(request)

  files = page.attached_files()
  files = [file_obj for file_obj in files if not file_obj.is_hidden]

  for item in files:
    ext = item.name.lower().split('.')[-1]
    item.icon = '/static/images/fileicons/%s.png' % ext

  is_editor = page.user_can_write(profile)

  if configuration.SYSTEM_THEME_NAME:
    template = 'themes/%s/page.html' % (configuration.SYSTEM_THEME_NAME)

  return utility.respond(request, template, {'page': page, 'files': files,
                                             'is_editor': is_editor})


def send_file(file_record, request):
  """Sends a given file to a user if they have access rights.

  Images can be transformed if GET parameter has been added to the URL:
  - size=<value in pixels> - resizes the image to the supplied value, applying
    the specified size to the image's longest dimension and preserving
    the original aspect ratio.
  - crop=<value in pixels> - the image will be cropped after resize to fit the
    specified size.
  For example, to crop an image, the image URL looks like this:
    http://example.com/image.jpg/?crop=200

  Args:
    file_record: The file to send to the user
    request: The Django request object

  Returns:
    A Django HttpResponse containing the requested file, or an error message.

  """
  profile = request.profile

  if not file_record.user_can_read(profile):
    logging.warning('User %s made an invalid attempt to access file %s' %
                    (profile.email, file_record.name))
    return utility.forbidden(request)

  content = None
  mimetype = file_record.blob_data.content_type
  file_ext = file_record.name.lower().split('.')[-1]

  if request.GET.get('size') and file_ext in utility.IMAGE_EXT:
    if not request.GET.get('size').isdigit():
      return utility.page_not_found(request)
    size = int(request.GET.get('size'))
    key = "thumbnail:%s?size=%s" % (request.path, size)
    thumbnail = utility.memcache_get(key)
    if thumbnail:
      content, mimetype = thumbnail
    else:
      content, mimetype = resize_image(file_record, size)
      utility.memcache_set(key, (content, mimetype))
  elif request.GET.get('crop') and file_ext in utility.IMAGE_EXT:
    if not request.GET.get('crop').isdigit():
      return utility.page_not_found(request)
    size = int(request.GET.get('crop'))
    key = "thumbnail:%s?crop=%s" % (request.path, size)
    thumbnail = utility.memcache_get(key)
    if thumbnail:
      content, mimetype = thumbnail
    else:
      content, mimetype = resize_image(file_record, size, crop=True)
      utility.memcache_set(key, (content, mimetype))

  response = http.HttpResponse(content=content, mimetype=mimetype)

  if not content:
    response['X-AppEngine-BlobKey'] = file_record.blob_key

  if not file_ext in utility.IMAGE_EXT + utility.FLASH_EXT:
    response['Content-Disposition'] = ('attachment; filename=%s' %
                                        file_record.name)

  expires = datetime.datetime.now() + configuration.FILE_CACHE_TIME
  response['Cache-Control'] = configuration.FILE_CACHE_CONTROL
  response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
  return response


def get_url(request, path_str):
  """Parse the URL and return the requested content to the user.

  Args:
    request: The Django request object.
    path_str: The URL path as a string

  Returns:
    A Django HttpResponse containing the requested page or file, or an error
    message.

  """
  def follow_url_forwards(base, path):
    """Follow the path forwards, returning the desired item."""
    if not base:
      return None
    if not path:
      utility.memcache_set('path:%s' % path_str, base)
      return base
    if len(path) == 1:
      attachment = base.get_attachment(path[0])
      if attachment:
        return attachment
    return follow_url_forwards(base.get_child(path[0]), path[1:])

  def follow_url_backwards(pre_path, post_path):
    """Traverse the path backwards to find a cached page or the root."""
    key = 'path:' + '/'.join(pre_path)
    item = utility.memcache_get(key)
    if item:
      return follow_url_forwards(item, post_path)
    if not pre_path:
      return follow_url_forwards(models.Page.get_root(), post_path)
    return follow_url_backwards(pre_path[:-1], [pre_path[-1]] + post_path)

  path = [dir_name for dir_name in path_str.split('/') if dir_name]
  item = follow_url_backwards(path, [])

  if isinstance(item, models.Page):
    return send_page(item, request)

  if isinstance(item, models.FileStore):
    return send_file(item, request)

  return utility.page_not_found(request)


def get_tree_data(request):
  """Returns the structure of the file hierarchy in JSON format.

  Args:
    request: The Django request object

  Returns:
    A Django HttpResponse object containing the file data.

  """

  def get_node_data(page):
    """A recursive function to output individual nodes of the tree."""
    page_id = str(page.key().id())
    data = {'title': page.title,
            'path': page.path,
            'id': page_id,
            'edit_url': urlresolvers.reverse(
                'views.admin.edit_page', args=[page_id]),
            'child_url': urlresolvers.reverse(
                'views.admin.new_page', args=[page_id]),
            'delete_url': urlresolvers.reverse(
                'views.admin.delete_page', args=[page_id])}
    children = []
    for child in page.page_children:
      if child.acl.user_can_read(request.profile):
        children.append(get_node_data(child))
    if children:
      data['children'] = children
    return data

  data = {'identifier': 'id', 'label': 'title',
          'items': [get_node_data(models.Page.get_root())]}

  return http.HttpResponse(simplejson.dumps(data), mimetype='application/json')


def page_list(request):
  """List all pages."""
  return utility.respond(request, 'sitemap')


def resize_image(file_record, size, crop=False):
  """Resizes the image maintaining the aspect ratio.

  Args:
    file_record: The image file to resize.
    size: The size (in pixels) to change the image dimensions to.
    crop: If True the image is cropped to fit the specified dimensions.

  Returns:
    A tuple of image data after the transformations have been performed on it
    and its mimetype.
  """
  content_type = file_record.blob_data.content_type
  img = images.Image(blob_key=file_record.blob_key)
  img.resize(width=size, height=size, crop_to_fit=crop)

  if content_type in ('image/png', 'image/gif'):
    thumbnail = img.execute_transforms(output_encoding=images.PNG)
    thumbnail_mimetype = 'image/png'
  elif content_type == 'image/webp':
    thumbnail = img.execute_transforms(output_encoding=images.WEBP)
    thumbnail_mimetype = 'image/webp'
  else:
    thumbnail = img.execute_transforms(output_encoding=images.JPEG)
    thumbnail_mimetype = 'image/jpeg'

  if crop:
    return thumbnail, thumbnail_mimetype

  # To prevent scaling up checking image dimensions
  metadata = img.get_original_metadata()
  if metadata['ImageWidth'] > size or metadata['ImageLength'] > size:
    return thumbnail, thumbnail_mimetype
  else:
    return None, content_type
