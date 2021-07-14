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

"""PyAMS_portal.portlets.html.skin module

This module defines renderers from rich text and code portlets.
"""

from zope.interface import Interface

from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.portlets.html import IHTMLPortletSettings, IRawPortletSettings
from pyams_portal.skin import PortletRenderer
from pyams_template.template import template_config
from pyams_utils import library
from pyams_utils.adapter import adapter_config
from pyams_utils.fanstatic import ExternalResource
from pyams_utils.interfaces.pygments import IPygmentsCodeConfiguration
from pyams_utils.interfaces.text import IHTMLRenderer
from pyams_utils.pygments import render_source


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


#
# Raw HTML portlet renderer
#


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, IRawPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/raw.pt', layer=IPyAMSLayer)
class RawPortletDefaultRenderer(PortletRenderer):
    """Raw HTML portlet renderer"""

    label = _("HTML source code (default)")
    weight = 1


#
# Formatted source code renderer
#

@adapter_config(name='source-code',
                required=(IPortalContext, IPyAMSLayer, Interface, IRawPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/raw-code.pt', layer=IPyAMSLayer)
class RawPortletSourceCodeRenderer(PortletRenderer):
    """Formatted source code portlet renderer"""

    label = _("Formatted source code")
    weight = 10

    settings_interface = IPygmentsCodeConfiguration

    @property
    def resources(self):
        """Fanstatic resources getter"""
        settings = self.renderer_settings
        path = 'get-pygments-style.css?style={}'.format(settings.style)
        resource = library.known_resources.get(path)
        if resource is None:
            resource = ExternalResource(library, path, resource_type='css')
            if library.library_nr is None:
                library.init_library_nr()
        yield resource

    @property
    def body(self):
        """Formatted body getter"""
        code = II18n(self.settings).query_attribute('body', request=self.request)
        if code:
            return render_source(code, self.renderer_settings)
        return ''


#
# ReStructuredText renderer
#

@adapter_config(name='rest',
                required=(IPortalContext, IPyAMSLayer, Interface, IRawPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/raw-code.pt', layer=IPyAMSLayer)
class RawPortletSourceRestRenderer(PortletRenderer):
    """ReStructured text portlet renderer"""

    label = _("ReStructured text")
    weight = 20

    @property
    def body(self):
        """Formatted body getter"""
        code = II18n(self.settings).query_attribute('body', request=self.request)
        if code:
            renderer = self.request.registry.queryMultiAdapter((code, self.request),
                                                               IHTMLRenderer, name='rest')
            if renderer is not None:
                return renderer.render()
        return ''


#
# Markdown renderer
#

@adapter_config(name='markdown',
                required=(IPortalContext, IPyAMSLayer, Interface, IRawPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/raw-code.pt', layer=IPyAMSLayer)
class RawPortletSourceMarkdownRenderer(PortletRenderer):
    """Markdown text portlet renderer"""

    label = _("Markdown text")
    weight = 30

    @property
    def body(self):
        """Formatted body getter"""
        code = II18n(self.settings).query_attribute('body', request=self.request)
        if code:
            renderer = self.request.registry.queryMultiAdapter((code, self.request),
                                                               IHTMLRenderer, name='markdown')
            if renderer is not None:
                return renderer.render()
        return ''


#
# Rich text portlet renderer
#

@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, IHTMLPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/html.pt', layer=IPyAMSLayer)
class HTMLPortletDefaultRenderer(PortletRenderer):
    """Rich text portlet renderer"""

    label = _("Rich text (default)")
