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

"""PyAMS_portal.zmi.layout module

This module defines all components required to handle layout of portal templates.
"""

import json

from pyramid.decorator import reify
from pyramid.renderers import render
from pyramid.view import view_config
from zope.copy import copy
from zope.interface import Interface, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalPortletsConfiguration, \
    IPortalTemplate, IPortalTemplateConfiguration, IPortalTemplateContainer, \
    IPortalTemplateContainerConfiguration, IPortlet, IPortletPreviewer, LOCAL_TEMPLATE_NAME, \
    MANAGE_TEMPLATE_PERMISSION
from pyams_portal.page import check_local_template
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_security.interfaces.base import FORBIDDEN_PERMISSION
from pyams_security.permission import get_edit_permission
from pyams_skin.interfaces.viewlet import IBreadcrumbItem, IHelpViewletManager
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.help import AlertMessage
from pyams_skin.viewlet.menu import MenuItem
from pyams_template.template import template_config
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import query_utility
from pyams_utils.traversing import get_parent
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm
from pyams_zmi.interfaces import IAdminLayer, IInnerAdminView
from pyams_zmi.interfaces.viewlet import IActionsViewletManager, IContentManagementMenu, \
    IContextAddingsViewletManager, IMenuHeader, IPropertiesMenu, ISiteManagementMenu
from pyams_zmi.utils import get_object_label
from pyams_zmi.zmi.viewlet.breadcrumb import AdminLayerBreadcrumbItem
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


@adapter_config(required=(IPortalTemplate, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def portal_template_menu_header(context, request, view, manager):  # pylint: disable=unused-argument
    """Portal template menu header"""
    return _("Portal template")


@viewletmanager_config(name='layout.menu',
                       context=IPortalTemplate, layer=IAdminLayer,
                       manager=IContentManagementMenu, weight=10,
                       provides=IPropertiesMenu,
                       permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateLayoutMenu(NavigationMenuItem):
    """Portal template layout menu"""

    label = _("Page layout")
    icon_class = 'far fa-object-group'
    href = '#layout.html'


@adapter_config(required=(IPortalTemplate, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class PortalTemplateBreadcrumbItem(AdminLayerBreadcrumbItem):
    """Portal template breadcrumb item"""

    @property
    def label(self):
        """Label getter"""
        return self.context.name


@pagelet_config(name='layout.html',
                context=IPortalTemplate, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
@template_config(template='templates/layout.pt', layer=IAdminLayer)
@implementer(IInnerAdminView)
class PortalTemplateLayoutView:  # pylint: disable=no-member
    """Portal template layout view"""

    @property
    def title(self):
        """View title getter"""
        translate = self.request.localizer.translate
        container = get_parent(self.context, IPortalTemplateContainer)
        if container is None:
            context = get_parent(self.context, IPortalContext)
            page = IPortalPage(context)
            if page.use_local_template:
                return _("Local template configuration")
            if page.template.name == LOCAL_TEMPLATE_NAME:
                return _("Inherited local template configuration")
            return translate(_("« {} » shared template configuration")).format(page.template.name)
        return translate(_("« {} » template configuration")).format(self.context.name)

    def get_template(self):
        """Template getter"""
        return self.context

    def get_context(self):
        """Context getter"""
        return self.context

    @property
    def can_change(self):
        """Change checker"""
        return self.request.has_permission(MANAGE_TEMPLATE_PERMISSION)

    @reify
    def template_configuration(self):
        """Template configuration getter"""
        return IPortalTemplateConfiguration(self.get_template())

    @reify
    def portlets_configuration(self):
        """Portlets configuration getter"""
        return IPortalPortletsConfiguration(self.get_context())

    @property
    def selected_portlets(self):
        """Selected portlets getter"""
        container = query_utility(IPortalTemplateContainer)
        configuration = IPortalTemplateContainerConfiguration(container)
        utility = self.request.registry.queryUtility
        return filter(lambda x: x is not None, [
            utility(IPortlet, name=portlet_name)
            for portlet_name in (configuration.toolbar_portlets or ())
        ])

    def get_portlet(self, name):
        """Portlet utility getter"""
        return self.request.registry.queryUtility(IPortlet, name=name)

    def get_portlet_add_label(self, portlet):
        """Portlet add label getter"""
        translate = self.request.localizer.translate
        return translate(_("Add component: {0}<br />"
                           "Drag and drop button to page template to "
                           "position new row")).format(translate(portlet.label).lower())

    def get_portlet_label(self, name):
        """Portlet label getter"""
        portlet = self.get_portlet(name)
        if portlet is not None:
            return self.request.localizer.translate(portlet.label)
        return self.request.localizer.translate(_("{{ missing portlet }}"))

    def get_portlet_preview(self, portlet_id):
        """Portlet preview getter"""
        configuration = self.portlets_configuration
        portlet_config = configuration.get_portlet_configuration(portlet_id)
        settings = portlet_config.settings
        previewer = self.request.registry.queryMultiAdapter(
            (self.get_context(), self.request, self, settings),
            IPortletPreviewer)
        if previewer is not None:
            previewer.update()
            return render('templates/portlet-preview.pt', {
                'config': portlet_config,
                'can_change': self.can_change,
                'can_delete': IPortalTemplate.providedBy(self.context) or
                              IPortalPage(self.context).use_local_template,
                'label': self.get_portlet_label(portlet_config.portlet_name),
                'portlet': previewer.render()
            }, request=self.request)
        return ''


#
# Rows views
#

@viewlet_config(name='add-template-row.menu',
                context=IPortalTemplate, layer=IAdminLayer, view=PortalTemplateLayoutView,
                manager=IContextAddingsViewletManager, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateRowAddMenu(MenuItem):
    """Portal template row add menu"""

    label = _("Add row...")
    icon_class = 'fas fa-indent'
    href = 'MyAMS.portal.template.addRow'


@viewlet_config(name='add-template-row.menu',
                context=IPortalContext, layer=IAdminLayer, view=PortalTemplateLayoutView,
                manager=IContextAddingsViewletManager, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextTemplateRowAddMenu(PortalTemplateRowAddMenu):
    """Portal context template row add menu"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        page = IPortalPage(context)
        if not page.use_local_template:
            return None
        return PortalTemplateRowAddMenu.__new__(cls)


@view_config(name='add-template-row.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='add-template-row.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def add_template_row(request):
    """Add template raw"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    return {'row_id': config.add_row()}


@view_config(name='set-template-row-order.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='set-template-row-order.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def set_template_row_order(request):
    """Set template rows order"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    row_ids = map(int, json.loads(request.params.get('rows')))
    config.set_row_order(row_ids)
    return {'status': 'success'}


@view_config(name='delete-template-row.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='delete-template-row.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def delete_template_row(request):
    """Delete template row"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    config.delete_row(int(request.params.get('row_id')))
    return {'status': 'success'}


#
# Convert local template to shared template
#

@viewlet_config(name='share-template.menu',
                context=IPortalContext, layer=IAdminLayer, view=PortalTemplateLayoutView,
                manager=IActionsViewletManager, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class LocalTemplateShareMenu(MenuItem):
    """Local template share menu"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        page = IPortalPage(context, None)
        if (page is None) or not page.use_local_template:
            return None
        templates = query_utility(IPortalTemplateContainer)
        if templates is None:
            return None
        if not request.has_permission(MANAGE_TEMPLATE_PERMISSION, context=templates):
            return None
        return MenuItem.__new__(cls)

    label = _("Share template")
    icon_class = 'fas fa-share'

    href = 'share-template.html'
    modal_target = True


class ILocalTemplateShareFormButtons(Interface):
    """Local template share form buttons"""

    share = SubmitButton(name='share',
                         title=_("Share template"))

    close = CloseButton(name='close',
                        title=_("Close"))


@ajax_form_config(name='share-template.html',
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextTemplateShareForm(AdminModalAddForm):
    """Local template share form"""

    @property
    def title(self):
        """Form title getter"""
        return get_object_label(self.context, self.request, self)

    legend = _("Share local template")

    fields = Fields(IPortalTemplate).select('name')
    buttons = Buttons(ILocalTemplateShareFormButtons)

    @property
    def edit_permission(self):
        return get_edit_permission(self.request, self.context, self, 'share')

    @handler(ILocalTemplateShareFormButtons['share'])
    def handle_share(self, action):
        """Share form button handler"""
        super().handle_add(self, action)

    def create(self, data):
        page = IPortalPage(self.context)
        return copy(page.local_template)

    def add(self, obj):
        templates = query_utility(IPortalTemplateContainer)
        oid = IUniqueID(obj).oid
        templates[oid] = obj
        page = IPortalPage(self.context)
        page.use_local_template = False
        page.shared_template = oid


@adapter_config(name='share',
                required=(IPortalContext, IAdminLayer, PortalContextTemplateShareForm),
                provides=IViewContextPermissionChecker)
class PortalContextTemplateSharePermissionChecker(ContextRequestViewAdapter):
    """Portal context share permission checker"""

    @property
    def edit_permission(self):
        """Edit permission getter"""
        page = IPortalPage(self.context, None)
        if (page is None) or not page.use_local_template:
            return FORBIDDEN_PERMISSION
        templates = query_utility(IPortalTemplateContainer)
        if templates is None:
            return FORBIDDEN_PERMISSION
        if not self.request.has_permission(MANAGE_TEMPLATE_PERMISSION, context=templates):
            return FORBIDDEN_PERMISSION
        return MANAGE_TEMPLATE_PERMISSION


@viewlet_config(name='share-template.help',
                context=IPortalContext, layer=IAdminLayer, view=PortalContextTemplateShareForm,
                manager=IHelpViewletManager, weight=100)
class PortalContextTemplateShareFormHelp(AlertMessage):
    """Portal context local template share form help"""

    status = 'info'
    _message = _("Sharing a local template will make a copy of it in shared templates utility.\n"
                 "Your page will then be configured to use this template, but your previous "
                 "local template will not be lost...")


@adapter_config(required=(IPortalContext, IAdminLayer, PortalContextTemplateShareForm),
                provides=IAJAXFormRenderer)
class PortalContextTemplateShareFormRenderer(ContextRequestViewAdapter):
    """Portal context template share form renderer"""

    @staticmethod
    def render(changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        return {
            'status': 'reload'
        }
