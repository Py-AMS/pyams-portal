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
from zope.interface import Invalid

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import HIDDEN_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalTemplate, \
    IPortalTemplateConfiguration, IPortalTemplateContainer, ISlot, ISlotConfiguration, \
    MANAGE_TEMPLATE_PERMISSION
from pyams_portal.page import check_local_template
from pyams_portal.zmi.layout import PortalTemplateLayoutView
from pyams_skin.viewlet.menu import MenuItem
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.registry import get_utility
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextAddingsViewletManager
from pyams_zmi.utils import get_object_label


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class PortalTemplateSlotMixinForm:
    """Portal template slot mixin form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        if IPortalTemplate.providedBy(self.context):
            container = get_utility(IPortalTemplateContainer)
            return '<small>{}</small><br />{}'.format(
                get_object_label(container, self.request, self),
                translate(_("« {} »  portal template")).format(self.context.name))
        return '<small>{}</small><br />{}'.format(
            get_object_label(self.context, self.request, self),
            translate(_("Local template")))


@viewlet_config(name='add-template-slot.menu',
                context=IPortalTemplate, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=20)
class PortalTemplateSlotAddMenu(MenuItem):
    """Portal template slot add menu"""

    label = _("Add slot...")
    icon_class = 'fas fa-columns'

    href = 'add-template-slot.html'
    modal_target = True


@viewlet_config(name='add-template-slot.menu',
                context=IPortalContext, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=20)
class PortalContextTemplateSlotAddMenu(PortalTemplateSlotAddMenu):
    """Portal context template slot add menu"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        page = IPortalPage(context)
        if not page.use_local_template:
            return None
        return PortalTemplateSlotAddMenu.__new__(cls)


@ajax_form_config(name='add-template-slot.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@ajax_form_config(name='add-template-slot.html',
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateSlotAddForm(PortalTemplateSlotMixinForm, AdminModalAddForm):  # pylint: disable=abstract-method
    """Portal template slot add form"""

    def __init__(self, context, request):
        check_local_template(context)
        super().__init__(context, request)

    legend = _("Add slot")

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
@adapter_config(required=(IPortalContext, IAdminLayer, PortalTemplateSlotAddForm),
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
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateSlotPropertiesEditForm(PortalTemplateSlotMixinForm, AdminModalEditForm):
    """Portal template slot properties edit form"""

    @property
    def legend(self):
        """Legend getter"""
        translate = self.request.localizer.translate
        return translate(_("« {} » slot properties")).format(self.get_content().slot_name)

    label_css_class = 'col-sm-6'
    input_css_class = 'col-sm-2'

    fields = Fields(ISlotConfiguration).omit('visible', 'portlet_ids')

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
        css_class = self.widgets.get('container_css_class')
        if css_class is not None:
            css_class.input_css_class = 'col-sm-6'
        css_class = self.widgets.get('css_class')
        if css_class is not None:
            css_class.input_css_class = 'col-sm-6'


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplateSlotPropertiesEditForm),
                provides=IAJAXFormRenderer)
@adapter_config(required=(IPortalContext, IAdminLayer, PortalTemplateSlotPropertiesEditForm),
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
             context=IPortalContext, request_type=IPyAMSLayer,
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
    return {'status': 'success'}


@view_config(name='switch-slot-visibility.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='switch-slot-visibility.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def switch_slot_visibility(request):
    """Switch slot visibility"""
    context = request.context
    check_local_template(context)
    params = request.params
    config = IPortalTemplateConfiguration(context)
    slot_config = config.get_slot_configuration(params.get('slot_name'))
    slot_config.visible = not slot_config.visible
    return {'status': slot_config.visible}


@view_config(name='get-slots-width.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='get-slots-width.json',
             context=IPortalContext, request_type=IPyAMSLayer,
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
             context=IPortalContext, request_type=IPyAMSLayer,
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
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def delete_template_slot(request):
    """Delete template slot"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    config.delete_slot(request.params.get('slot_name'))
    return {'status': 'success'}
