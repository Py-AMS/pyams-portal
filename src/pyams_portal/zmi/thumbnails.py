#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_portal.zmi.thumbnails module

This module defines ZMI components which are used to handle
selection of renderers thumbnails.
"""

import os
from cgi import FieldStorage
from datetime import datetime

from persistent.mapping import PersistentMapping
from zope.dublincore.interfaces import IZopeDublinCore
from zope.schema.interfaces import IDict

from pyams_file.file import EXTENSIONS_THUMBNAILS
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_form.ajax import ajax_form_config
from pyams_form.browser.widget import HTMLFormElement
from pyams_form.converter import BaseDataConverter
from pyams_form.field import Fields
from pyams_form.interfaces import IDataConverter, INPUT_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_form.template import widget_template_config
from pyams_form.util import to_bytes
from pyams_form.widget import FieldWidget, Widget
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import HIDDEN_RENDERER_NAME, IPortalTemplateContainer, IPortlet, IPortletConfiguration, \
    IPortletRenderer, IPortletsRenderersThumbnails, MANAGE_TEMPLATE_PERMISSION
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config, get_adapter_weight
from pyams_utils.factory import create_object
from pyams_utils.interfaces.form import NOT_CHANGED, NO_VALUE, TO_BE_DELETED
from pyams_utils.registry import get_utility
from pyams_utils.size import get_human_size
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IPropertiesMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_portal import _


@widget_template_config(mode=INPUT_MODE,
                        template='templates/thumbnails-widget.pt',
                        layer=IAdminLayer)
class RenderersThumbnailsWidget(HTMLFormElement, Widget):
    """Renderers thumbnails widget"""

    klass = 'thumbnails-widget'

    def __init__(self, request):
        super().__init__(request)
        container = get_utility(IPortalTemplateContainer)
        self.thumbnails = IPortletsRenderersThumbnails(container)

    def extract(self, default=NO_VALUE):
        values = PersistentMapping()
        params = self.request.params
        marker = params.get(f'{self.name}__marker')
        if marker is None:
            return NO_VALUE
        for portlet_name, portlet in self.get_portlets():
            for renderer_name, renderer in self.get_renderers(portlet):
                name = f'{portlet_name}::{renderer_name}' if renderer_name else portlet_name
                deleted_name = f'{name}__deleted'
                deleted = params.get(deleted_name)
                if deleted:
                    value = TO_BE_DELETED
                else:
                    thumb = params.get(f'{name}__thumbnail')
                    if (thumb is None) or (thumb is NOT_CHANGED) or (thumb == ''):
                        value = NOT_CHANGED
                    elif isinstance(thumb, FieldStorage):
                        value = thumb.filename, thumb.file
                    elif isinstance(thumb, tuple):
                        value = thumb
                    else:
                        value = to_bytes(thumb)
                values[name] = value
        return values

    def get_portlets(self):
        """Portlets getter"""
        registry = self.request.registry
        translate = self.request.localizer.translate
        yield from sorted(registry.getUtilitiesFor(IPortlet),
                          key=lambda x: translate(x[1].label))

    def get_renderers(self, portlet):
        """Portlet renderers getter"""
        request = self.request
        registry = request.registry
        configuration = create_object(IPortletConfiguration, portlet=portlet)
        yield from filter(lambda x: x[0] != HIDDEN_RENDERER_NAME,
                          sorted(registry.getAdapters((request.root, request, None,
                                                       configuration.settings), IPortletRenderer),
                                 key=get_adapter_weight))

    def get_value(self, portlet_name, renderer_name):
        """Portlet renderer thumbnail value getter"""
        return self.thumbnails.get_thumbnail(portlet_name, renderer_name)

    def get_thumbnail(self, value, geometry='128x128'):
        """Image thumbnail getter"""
        thumbnails = IThumbnails(value, None)
        if thumbnails is not None:
            display = thumbnails.get_thumbnail(geometry)  # pylint: disable=assignment-from-no-return
            if display is not None:
                dc = IZopeDublinCore(display, None)  # pylint: disable=invalid-name
                if dc is None:
                    dc = IZopeDublinCore(value, None)
                if dc is None:
                    timestamp = datetime.utcnow().timestamp()
                else:
                    timestamp = dc.modified.timestamp()  # pylint: disable=no-member
                return '{}?_={}'.format(absolute_url(display, self.request),
                                        timestamp)
        _name, ext = os.path.splitext(value.filename)
        return '/--static--/pyams_file/img/{}'.format(
            EXTENSIONS_THUMBNAILS.get(ext, 'unknown.png'))

    def get_human_size(self, value):
        """Human size getter"""
        return get_human_size(value.get_size(), self.request)


def RenderersThumbnailsFieldWidget(field, request):
    """Renderers thumbnails field widget factory"""
    return FieldWidget(field, RenderersThumbnailsWidget(request))


@adapter_config(required=(IDict, RenderersThumbnailsWidget),
                provides=IDataConverter)
class RenderersThumbnailsDataConverter(BaseDataConverter):
    """Renderers thumbnails data converter"""

    def to_field_value(self, value):
        """Widget to field converter"""
        return value


@viewlet_config(name='renderers-thumbnails.menu',
                context=IPortalTemplateContainer, layer=IAdminLayer,
                manager=IPropertiesMenu, weight=20,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplateContainerThumbnailsMenu(NavigationMenuItem):
    """Portal template container thumbnails menu"""

    label = _("Renderers thumbnails")

    href = '#renderers-thumbnails.html'


@ajax_form_config(name='renderers-thumbnails.html',
                  context=IPortalTemplateContainer, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatesContainerThumbnailsEditForm(AdminEditForm):
    """Portal templates container renderers thumbnails edit form"""

    title = _("Portlets renderers thumbnails")
    legend = _("Thumbnails of portlets renderers")

    fields = Fields(IPortletsRenderersThumbnails)
    fields['thumbnails'].widget_factory = RenderersThumbnailsFieldWidget


@adapter_config(required=(IPortalTemplateContainer, IAdminLayer, PortalTemplatesContainerThumbnailsEditForm),
                provides=IAJAXFormRenderer)
class PortalTemplatesContainerThumbnailsEditFormRenderer(ContextRequestViewAdapter):
    """Portal templates container renderers thumbnails edit form renderer"""

    def render(self, changes):
        if changes is None:
            return None
        return {
            'status': 'reload',
            'message': self.request.localizer.translate(self.view.success_message)
        }
