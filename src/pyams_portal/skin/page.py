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

"""PyAMS_portal.skin.page module

This module defines base classes for portal context index pages.
"""

__docformat__ = 'restructuredtext'

from pyramid.decorator import reify
from pyramid.exceptions import NotFound
from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalPortletsConfiguration, \
    IPortalTemplateConfiguration, IPortlet, IPortletCSSClass, IPortletRenderer, PREVIEW_MODE
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_template.template import layout_config, template_config
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.tales import ITALESExtension
from pyams_utils.request import get_annotations
from pyams_utils.traversing import get_parent
from pyams_workflow.interfaces import IWorkflowPublicationInfo


class BasePortalContextIndexPage:
    """Base portal context index page"""

    portlets = None

    def update(self):
        """Page update"""
        super().update()  # pylint: disable=no-member
        # extract all renderers list
        context = self.context  # pylint: disable=no-member
        request = self.request  # pylint: disable=no-member
        self.portlets = {}
        template_configuration = self.template_configuration
        portlets_configuration = self.portlet_configuration
        for row_id in range(template_configuration.rows):
            for slot_name in template_configuration.get_slots(row_id):
                for portlet_id in template_configuration.slot_config[slot_name].portlet_ids:
                    settings = portlets_configuration \
                        .get_portlet_configuration(portlet_id).settings
                    renderer = request.registry.queryMultiAdapter(
                        (context, request, self, settings), IPortletRenderer,
                        name=settings.renderer)
                    if renderer is not None:
                        renderer.update()
                        self.portlets[portlet_id] = renderer

    @reify
    def page(self):
        """Portal page getter"""
        return IPortalPage(self.context)  # pylint: disable=no-member

    @reify
    def template_configuration(self):
        """Template configuration getter"""
        return IPortalTemplateConfiguration(self.page.template)

    @reify
    def portlet_configuration(self):
        """Portlet configuration getter"""
        return IPortalPortletsConfiguration(self.context)  # pylint: disable=no-member

    def get_portlet(self, name):
        """Portlet getter"""
        return self.request.registry.queryUtility(IPortlet, name=name)  # pylint: disable=no-member

    def get_portlet_css_class(self, portlet_id):
        """Portlet CSS class getter"""
        configuration = self.portlet_configuration.get_portlet_configuration(portlet_id)
        portlet = self.get_portlet(configuration.portlet_name)
        if portlet is not None:
            request = self.request  # pylint: disable=no-member
            return request.registry.queryMultiAdapter((portlet, request),
                                                      IPortletCSSClass, default='')
        return None

    def render_portlet(self, portlet_id, template_name=''):
        """Render given portlet"""
        renderer = self.portlets.get(portlet_id)
        if renderer is None:
            return ''
        return renderer.render(template_name)


@pagelet_config(name='',
                context=IPortalContext, layer=IPyAMSLayer)
@layout_config(template='templates/layout.pt', layer=IPyAMSLayer)
@template_config(template='templates/pagelet.pt', layer=IPyAMSLayer)
class PortalContextIndexPage(BasePortalContextIndexPage):
    """Portal context index page"""

    def update(self):
        wf_info = IWorkflowPublicationInfo(self.context, None)  # pylint: disable=no-member
        if (wf_info is not None) and not wf_info.is_visible(self.request):  # pylint: disable=no-member
            raise NotFound()
        super().update()


@pagelet_config(name='preview.html',
                context=IPortalContext, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
class PortalContextPreviewPage(PortalContextIndexPage):
    """Portal context preview page"""

    def update(self):
        # Bypass publication status in preview
        get_annotations(self.request)[PREVIEW_MODE] = True  # pylint: disable=no-member
        super(PortalContextIndexPage, self).update()  # pylint: disable=bad-super-call


@adapter_config(name='template_container_class',
                required=(Interface, IPyAMSLayer, Interface),
                provides=ITALESExtension)
class TemplateContainerClassTALESExtension(ContextRequestViewAdapter):
    """Template class TALES extension"""

    def render(self, context=None, default=''):
        """Extension renderer"""
        if context is None:
            context = self.context
        result = default
        parent = get_parent(context, IPortalContext)
        page = IPortalPage(parent, None)
        if page is not None:
            template = page.template
            if template is not None:
                result = template.css_class or result
        return result
