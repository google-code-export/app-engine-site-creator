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

CKEDITOR.plugins.add( 'gadget',
{
    lang : [ 'en', 'pl' ],

    init : function( editor )
    {
        editor.addCommand( 'gadgetDialog', new CKEDITOR.dialogCommand( 'gadgetDialog' ) );
        editor.ui.addButton( 'Gadget',
        {
            label : editor.lang.gadget.Label,
            command : 'gadgetDialog',
            icon : this.path + 'gadget.png'
        } );
        CKEDITOR.dialog.add( 'gadgetDialog', function( editor )
        {
            return {
                title : editor.lang.gadget.Title,
                minWidth : 285,
                minHeight : 140,
                resizable : CKEDITOR.DIALOG_RESIZE_NONE,
                contents :
                [
                    {
                        id : 'properties',
                        elements :
                        [
                            {
                                type : 'text',
                                id : 'url',
                                label : editor.lang.gadget.Url,
                                validate : CKEDITOR.dialog.validate.notEmpty( editor.lang.gadget.ErrNoUrl )
                            },
                            {
                                type : 'text',
                                id : 'height',
                                style : 'width:95px',
                                label : editor.lang.gadget.Height,
                                validate : CKEDITOR.dialog.validate.notEmpty( editor.lang.gadget.ErrNoHeight )
                            },
                            {
                                type : 'text',
                                id : 'width',
                                style : 'width:95px',
                                label : editor.lang.gadget.Width,
                                validate : CKEDITOR.dialog.validate.notEmpty( editor.lang.gadget.ErrNoWidth )
                            }
                        ]
                    }
                ],
                onOk : function()
                {
                    var dialog = this;
                    var gadget = editor.document.createElement( 'iframe' );
                    gadget.setAttribute( 'src', dialog.getValueOf( 'properties', 'url' ) );
                    gadget.setAttribute( 'scrolling', 'no' );
                    gadget.setStyles({
                        'height' : dialog.getValueOf( 'properties', 'height' ) + 'px',
                        'width' : dialog.getValueOf( 'properties', 'width' ) + 'px',
                        'border' : '0px' });
                    editor.insertElement( gadget );
                }
            };
        } );
    }
} );

