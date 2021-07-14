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

"""PyAMS_portal.zmi.widget module

This module defines a custom widget used to select portlet renderer, which
provides access to custom renderer settings, if any.
"""

from pyams_form.browser.select import SelectWidget
from pyams_form.interfaces import INPUT_MODE
from pyams_form.template import widget_template_config
from pyams_form.widget import FieldWidget
from pyams_zmi.interfaces import IAdminLayer

__docformat__ = 'restructuredtext'


@widget_template_config(mode=INPUT_MODE,
                        template='templates/renderer-input.pt',
                        layer=IAdminLayer)
class PortletRendererWidget(SelectWidget):
    """Portlet renderer widget"""

    @property
    def show_renderer_properties(self):
        """Getter to check access to renderer properties action"""
        renderer = self.context.get_renderer(self.request)
        return (renderer is not None) and (renderer.settings_interface is not None)


def PortletRendererFieldWidget(field, request):  # pylint: disable=invalid-name
    """Portlet renderer field widget"""
    return FieldWidget(field, PortletRendererWidget(request))
