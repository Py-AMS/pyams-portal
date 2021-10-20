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

"""PyAMS_portal.zmi.container module

This module defines components used for portal templates container management.
"""

from pyramid.view import view_config
from zope.interface import Interface

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IInnerSubForm
from pyams_form.subform import InnerEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_portal.interfaces import IPortalTemplateContainer, \
    IPortalTemplateContainerConfiguration, MANAGE_TEMPLATE_PERMISSION
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_site.interfaces import ISiteRoot
from pyams_skin.interfaces.viewlet import IBreadcrumbItem
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.registry import get_utility, query_utility
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IControlPanelMenu, IMenuHeader, IPropertiesMenu, \
    ISiteManagementMenu
from pyams_zmi.table import NameColumn, Table, TableAdminView, TableElementEditor, TrashColumn
from pyams_zmi.zmi.viewlet.breadcrumb import AdminLayerBreadcrumbItem
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


@viewlet_config(name='portal-templates.menu',
                context=ISiteRoot, layer=IAdminLayer,
                manager=IControlPanelMenu, weight=50,
                permission=VIEW_SYSTEM_PERMISSION)
class PortalTemplatesMenu(NavigationMenuItem):
    """Portal templates menu"""

    label = _("Portal templates")
    icon_class = 'fas fa-table'

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        container = query_utility(IPortalTemplateContainer)
        if (container is None) or not container.show_home_menu:
            return None
        if not request.has_permission(MANAGE_TEMPLATE_PERMISSION, context=container):
            return None
        return NavigationMenuItem.__new__(cls)

    def get_href(self):
        """Menu URL getter"""
        container = get_utility(IPortalTemplateContainer)
        return absolute_url(container, self.request, 'admin')


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, Interface),
                provides=IObjectLabel)
def portal_template_container_label(context, request, view):
    """Portal template label getter"""
    return request.localizer.translate(_("Portal templates"))


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def portal_templates_container_header(context, request, view, manager):  # pylint: disable=unused-argument
    """Portal templates container menu header"""
    return _("Portal templates")


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, Interface),
                provides=IBreadcrumbItem)
class PortalTemplatesContainerBreadcrumbItem(AdminLayerBreadcrumbItem):
    """Portal templates container breadcrumb item"""

    label = _("Portal templates")


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, Interface),
                provides=ITableElementEditor)
class PortalTemplatesContainerElementEditor(TableElementEditor):
    """Portal templates container element editor"""

    view_name = 'admin#templates-list.html'
    modal_target = False

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        if not request.has_permission(MANAGE_TEMPLATE_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)


@viewletmanager_config(name='templates-list.menu',
                       context=IPortalTemplateContainer, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=10,
                       permission=MANAGE_TEMPLATE_PERMISSION,
                       provides=IPropertiesMenu)
class PortalTemplatesContainerListMenu(NavigationMenuItem):
    """Portal templates container list menu"""

    label = _("Templates list")
    icon_class = 'fas fa-table'
    href = '#templates-list.html'


class PortalTemplatesContainerTable(Table):
    """Portal templates container table"""

    display_if_empty = True


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, PortalTemplatesContainerTable),
                provides=IValues)
class PortalTemplatesContainerTableValues(ContextRequestViewAdapter):
    """Portal templates container table values adapter"""

    @property
    def values(self):
        """Portal templates container table values getter"""
        yield from self.context.values()


@adapter_config(name='name',
                required=(IPortalTemplateContainer, IAdminLayer, PortalTemplatesContainerTable),
                provides=IColumn)
class PortalTemplatesContainerNameColumn(NameColumn):
    """Portal templates container table name column"""


@adapter_config(name='trash',
                required=(IPortalTemplateContainer, IAdminLayer, PortalTemplatesContainerTable),
                provides=IColumn)
class PortalTemplatesContainerTrashColumn(TrashColumn):
    """Portal templates container table trash column"""

    permission = MANAGE_TEMPLATE_PERMISSION


@pagelet_config(name='templates-list.html',
                context=IPortalTemplateContainer, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatesContainerListView(TableAdminView):
    """Portal templates container list view"""

    title = _("Portal templates")
    table_class = PortalTemplatesContainerTable
    table_label = _("List of portal templates")

    @property
    def back_url(self):
        """Form back URL getter"""
        return absolute_url(self.request.root, self.request, 'admin#utilities.html')

    back_url_target = None


@view_config(name='delete-element.json',
             context=IPortalTemplateContainer, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def delete_portal_template(request):
    """Delete portal template"""
    return delete_container_element(request)


#
# Portlets container configuration
#

@viewlet_config(name='configuration.menu',
                context=IPortalTemplateContainer, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateContainerConfigurationMenu(NavigationMenuItem):
    """Portal template container configuration menu"""

    label = _("Configuration")

    href = '#configuration.html'


@ajax_form_config(name='configuration.html',
                  context=IPortalTemplateContainer, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateContainerConfigurationForm(AdminEditForm):
    """Portal template container configuration form"""

    title = _("Templates container")
    legend = _("Template selected portlets")

    fields = Fields(IPortalTemplateContainerConfiguration)


@adapter_config(name='home-menu',
                required=(IPortalTemplateContainer, IAdminLayer,
                          PortalTemplateContainerConfigurationForm),
                provides=IInnerSubForm)
class PortalTemplateContainerPropertiesEditForm(InnerEditForm):
    """Portal template container properties edit form"""

    legend = _("Management interface")

    fields = Fields(IPortalTemplateContainer['show_home_menu'])
