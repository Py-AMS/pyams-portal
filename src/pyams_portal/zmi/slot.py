#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_portal.zmi.slot module

This module provides slots management views.
"""

import json

from pyramid.events import subscriber
from pyramid.view import view_config
from zope.interface import Interface, Invalid, alsoProvides

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import HIDDEN_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent, IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalPage, IPortalTemplate, \
    IPortalTemplateConfiguration, IPortalTemplateContainer, ISlot, ISlotConfiguration, \
    MANAGE_TEMPLATE_PERMISSION
from pyams_portal.page import check_local_template
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.registry import get_utility
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm, FormGroupSwitcher
from pyams_zmi.interfaces import IAdminLayer, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class PortalTemplateSlotMixinForm:  # pylint: disable=no-member
    """Portal template slot mixin form"""


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateSlotMixinForm),
                provides=IFormTitle)
@adapter_config(required=(IPortalPage, IAdminLayer, PortalTemplateSlotMixinForm),
                provides=IFormTitle)
def portal_template_slot_form_title(context, request, form):
    """Portal template slot form title"""
    translate = request.localizer.translate
    if IPortalTemplate.providedBy(context):
        container = get_utility(IPortalTemplateContainer)
        return TITLE_SPAN_BREAK.format(
            get_object_label(container, request, form),
            translate(_("Portal template: {}")).format(context.name))
    return TITLE_SPAN_BREAK.format(
        get_object_label(context.__parent__, request, form),
        translate(_("Local template")))


@ajax_form_config(name='add-template-slot.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@ajax_form_config(name='add-template-slot.html',
                  context=IPortalPage, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateSlotAddForm(PortalTemplateSlotMixinForm, AdminModalAddForm):  # pylint: disable=abstract-method
    """Portal template slot add form"""

    def __init__(self, context, request):
        check_local_template(context)
        super().__init__(context, request)

    subtitle = _("New slot")
    legend = _("New slot properties")

    fields = Fields(ISlot)

    def update_widgets(self, prefix=None):
        super().update_widgets()
        row_id = self.request.params.get('{0}{1}row_id'.format(self.prefix,
                                                               self.widgets.prefix))
        if row_id:
            row_id_widget = self.widgets.get('row_id')
            if row_id_widget is not None:
                row_id_widget.value = str(int(row_id) + 1)
                row_id_widget.mode = HIDDEN_MODE

    def create_and_add(self, data):
        data = data.get(self, {})
        return self.create(data)

    def create(self, data):
        config = IPortalTemplateConfiguration(self.context)
        row_id = data.get('row_id')
        if row_id:
            row_id = row_id - 1
        return config.add_slot(data.get('name'), row_id)


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateSlotAddForm),
                provides=IFormTitle)
@adapter_config(required=(IPortalPage, IAdminLayer, PortalTemplateSlotAddForm),
                provides=IFormTitle)
def portal_template_slot_add_form_title(context, request, form):
    """Portal template slot add form title"""
    translate = request.localizer.translate
    if IPortalTemplate.providedBy(context):
        container = get_utility(IPortalTemplateContainer)
        return TITLE_SPAN_BREAK.format(
            get_object_label(container, request, form),
            translate(_("Portal template: {}")).format(context.name))
    return TITLE_SPAN_BREAK.format(
        get_object_label(context.__parent__, request, form),
        translate(_("Local template")))


@subscriber(IDataExtractedEvent, form_selector=PortalTemplateSlotAddForm)
def handle_new_slot_data_extraction(event):
    """Handle new slot form data extraction"""
    config = IPortalTemplateConfiguration(event.form.context)
    data = event.data
    name = data.get('name')
    if name in config.slot_names:
        event.form.widgets.errors += (Invalid(_("Specified name is already used!")),)
    row_id = data.get('row_id')
    if row_id is not None:
        try:
            row_id = int(row_id)
        except ValueError:
            event.form.widgets.errors += (Invalid(_("Row ID must be an integer value!")),)
        else:
            if not 0 < row_id <= config.rows:
                translate = event.form.request.localizer.translate
                event.form.widgets.errors += (Invalid(translate(_("Row ID must be between 1 "
                                                                  "and {0}!")).format(
                    config.rows)),)


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateSlotAddForm),
                provides=IAJAXFormRenderer)
@adapter_config(required=(IPortalPage, IAdminLayer, PortalTemplateSlotAddForm),
                provides=IAJAXFormRenderer)
class PortalTemplateSlotAddFormAJAXRenderer(ContextRequestViewAdapter):
    """Portal template slot add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        return {
            'status': 'success',
            'callback': 'MyAMS.portal.template.addSlotCallback',
            'options': {
                'row_id': changes[0],
                'slot_name': changes[1]
            }
        }


@ajax_form_config(name='slot-properties.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@ajax_form_config(name='slot-properties.html',
                  context=IPortalPage, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateSlotPropertiesEditForm(PortalTemplateSlotMixinForm, AdminModalEditForm):
    """Portal template slot properties edit form"""

    @property
    def subtitle(self):
        """Subtitle getter"""
        translate = self.request.localizer.translate
        return translate(_("Slot: {}")).format(self.get_content().slot_name)

    legend = _("Slot properties")

    label_css_class = 'col-sm-6'
    input_css_class = 'col-sm-2'

    fields = Fields(ISlotConfiguration).omit('visible', 'portlet_ids', 'prefix', 'suffix')

    def __init__(self, context, request):
        check_local_template(context)
        super().__init__(context, request)
        self.config = IPortalTemplateConfiguration(self.context)

    def get_content(self):
        """Content getter"""
        slot_name = self.request.params.get('{0}widgets.slot_name'.format(self.prefix))
        return self.config.slot_config[slot_name]

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        slot_name = self.widgets.get('slot_name')
        if slot_name is not None:
            slot_name.mode = HIDDEN_MODE
        for name in ('container_css_class', 'css_class', 'portlets_css_class'):
            widget = self.widgets.get(name)
            if widget is not None:
                widget.input_css_class = 'col-sm-6'


@adapter_config(name='html-codes',
                required=(Interface, IAdminLayer, PortalTemplateSlotPropertiesEditForm),
                provides=IGroup)
class PortalTemplateSlotPropertiesHTMLCodes(FormGroupSwitcher):
    """Portal template slot properties HTML codes"""

    legend = _("HTML codes")
    fields = Fields(ISlotConfiguration).select('prefix', 'suffix')
    switcher_mode = 'always'

    def update_widgets(self, prefix=None, use_form_mode=True):
        super().update_widgets(prefix, use_form_mode)
        for name in ('prefix', 'suffix'):
            widget = self.widgets.get(name)
            if widget is not None:
                widget.add_class('height-100')
                widget.widget_css_class = "editor height-100px"
                widget.object_data = {
                    'ams-filename': 'prefix.html'
                }
                alsoProvides(widget, IObjectData)


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateSlotPropertiesEditForm),
                provides=IAJAXFormRenderer)
@adapter_config(required=(IPortalPage, IAdminLayer, PortalTemplateSlotPropertiesEditForm),
                provides=IAJAXFormRenderer)
class PortalTemplatePropertiesEditFormAJAXRenderer(ContextRequestViewAdapter):
    """Portal template slot properties edit form JSON renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        form = self.view
        slot_name = form.widgets['slot_name'].value
        slot_config = form.config.slot_config[slot_name]
        return {
            'status': 'success',
            'callback': 'MyAMS.portal.template.editSlotCallback',
            'options': {
                'slot_name': slot_name,
                'width': slot_config.get_width(),
                'css': slot_config.css_class or ''
            }
        }


@view_config(name='set-template-slot-order.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='set-template-slot-order.json',
             context=IPortalPage, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def set_template_slot_order(request):
    """Set template slots order"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    order = json.loads(request.params.get('order'))
    for key in order.copy().keys():
        order[int(key)] = order.pop(key)
    config.set_slot_order(order)
    return {
        'status': 'success'
    }


@view_config(name='switch-slot-visibility.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='switch-slot-visibility.json',
             context=IPortalPage, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def switch_slot_visibility(request):
    """Switch slot visibility"""
    context = request.context
    check_local_template(context)
    params = request.params
    config = IPortalTemplateConfiguration(context)
    slot_config = config.get_slot_configuration(params.get('slot_name'))
    slot_config.visible = not slot_config.visible
    return {
        'status': slot_config.visible
    }


@view_config(name='get-slots-width.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='get-slots-width.json',
             context=IPortalPage, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def get_template_slots_width(request):
    """Get template slots width"""
    context = request.context
    config = IPortalTemplateConfiguration(context)
    return config.get_slots_width(request.params.get('device'))


@view_config(name='set-slot-width.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='set-slot-width.json',
             context=IPortalPage, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def set_template_slot_width(request):
    """Set template slot width"""
    context = request.context
    check_local_template(context)
    params = request.params
    config = IPortalTemplateConfiguration(context)
    config.set_slot_width(params.get('slot_name'),
                          params.get('device'),
                          int(params.get('width')))
    return config.get_slots_width(params.get('device'))


@view_config(name='delete-template-slot.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='delete-template-slot.json',
             context=IPortalPage, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def delete_template_slot(request):
    """Delete template slot"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    config.delete_slot(request.params.get('slot_name'))
    return {
        'status': 'success'
    }
