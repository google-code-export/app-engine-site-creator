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

"""Defines the url patterns for the application."""

# pylint: disable-msg=C0103,C0301

from django.conf.urls import defaults

urlpatterns = defaults.patterns(
    'aesc.views',
    defaults.url(r'^admin/$', 'admin.index', name='admin-index'),
    defaults.url(r'^admin/recent/$', 'admin.recently_modified', name='admin-recently-modified'),
    defaults.url(r'^admin/new/(\d*)$', 'admin.new_page', name='admin-new-page'),
    defaults.url(r'^admin/edit/sidebar/$', 'admin.edit_sidebar', name='admin-edit-sidebar'),
    defaults.url(r'^admin/edit/add_to_sidebar/(\d+)$', 'admin.add_to_sidebar', name='admin-add-to-sidebar'),
    defaults.url(r'^admin/edit/user/([^\s/]*)$', 'admin.edit_user', name='admin-edit-user'),
    defaults.url(r'^admin/users/$', 'admin.filter_users', name='admin-filter-users'),
    defaults.url(r'^admin/users/listgroups/$', 'admin.list_groups', name ='admin-list-groups'),
    defaults.url(r'^admin/users/newgroup/$', 'admin.new_group', name='admin-new-group'),
    defaults.url(r'^admin/users/addtogroup/(\d+)/([^\s/]*)$', 'admin.add_to_group', name='admin-add-to-group'),
    defaults.url(r'^admin/users/removefromgroup/(\d+)/([^\s/]*)$', 'admin.remove_from_group', name='admin-remove-from-group'),
    defaults.url(r'^admin/users/editgroup/([\w\-]+)$', 'admin.edit_group', name='admin-edit-group'),
    defaults.url(r'^admin/users/deletegroup/([\w\-]+)$', 'admin.delete_group', name='admin-delete-group'),
    defaults.url(r'^admin/users/bygroup/([\w\-]*)$', 'admin.view_group', name='admin-view-group'),
    defaults.url(r'^admin/editacl$', 'admin.edit_acl', name='admin-edit-acl'),
    defaults.url(r'^admin/bulkeditusers/$', 'admin.bulk_edit_users', name='admin-bulk-edit-users'),
    defaults.url(r'^admin/exportusers/$', 'admin.export_users', name='admin-export-users'),
    defaults.url(r'^admin/edit/(\d+)/$', 'admin.edit_page', name='admin-edit-page'),
    defaults.url(r'^admin/deletepage/([^\s]+)/$', 'admin.delete_page', name='admin-delete-page'),
    defaults.url(r'^admin/download/([\w\-]+).html$', 'admin.download_page_html', name='admin-download-page-html'),
    defaults.url(r'^admin/addfile/$', 'admin.upload_file', name='admin-upload-file'),
    defaults.url(r'^admin/deletefile/([\w\-]+)/([^\s/]+)$', 'admin.delete_file', name='admin-delete-file'),
    defaults.url(r'^admin/help/$', 'admin.get_help', name='admin-get-help'),
    defaults.url(r'^admin/memcache_info/$', 'admin.display_memcache_info', name='admin-display-memcache-info'),
    defaults.url(r'^admin/memcache_info/flush/$', 'admin.flush_memcache_info', name='admin-flush-memcache-info'),
    defaults.url(r'^_treedata/$', 'main.get_tree_data', name='get-tree-data'),
    defaults.url(r'^sitemap/$', 'main.page_list', name='page-list'),
    defaults.url(r'^(.*)$', 'main.get_url', name='get-url'),
)
