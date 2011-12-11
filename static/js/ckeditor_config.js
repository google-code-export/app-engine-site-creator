/*
 * Copyright 2008 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var pluginPath = '/static/js/plugins/';

CKEDITOR.plugins.addExternal('gadget', pluginPath+'gadget/');

CKEDITOR.editorConfig = function( config )
{
  config.skin = 'v2';

  config.extraPlugins = 'gadget';

  config.toolbar_AESC_Toolbar = [
    { name: 'tools', items : ['Maximize','Source'] },
    { name: 'clipboard', items : ['Undo','Redo'] },
    { name: 'editing', items : ['Find','Replace'] },
    { name: 'basicstyles', items : ['Bold','Italic','Underline','Strike'] },
    { name: 'paragraph', items : ['NumberedList','BulletedList','-','Outdent',
    'Indent','-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'] },
    { name: 'links', items : ['Link','Unlink'] },
    { name: 'insert', items : ['Gadget','Image','Flash','Table','SpecialChar'] },
    '/',
    { name: 'styles', items : ['Styles','Format','Font','FontSize'] },
    { name: 'colors', items : ['TextColor','BGColor'] } // No comma for the last row.
  ];
};
