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

"""PyAMS_portal.portlets.html.zmi module

This module defines HTML and code portlets management components.
"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface

from pyams_form.interfaces.form import IInnerSubForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer
from pyams_portal.portlets.html import IHTMLPortletSettings, IRawPortletSettings
from pyams_portal.zmi import PortletPreviewer
from pyams_portal.zmi.interfaces import IPortletConfigurationEditor
from pyams_portal.zmi.portlet import PortletConfigurationEditForm
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_zmi.interfaces import IAdminLayer


@adapter_config(name='configuration',
                required=(IRawPortletSettings, IAdminLayer, IPortletConfigurationEditor),
                provides=IInnerSubForm)
class RawPortletSettingsEditForm(PortletConfigurationEditForm):
    """Raw portlet settings edit form"""

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        body = self.widgets.get('body')
        if body is not None:
            body.add_widgets_class('height-100')
            body.widget_css_class = 'editor height-400px'


@adapter_config(required=(Interface, IPyAMSLayer, Interface, IRawPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/raw-preview.pt', layer=IPyAMSLayer)
class RawPortletPreviewer(PortletPreviewer):
    """Raw HTML portlet previewer"""


@adapter_config(required=(Interface, IPyAMSLayer, Interface, IHTMLPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/html-preview.pt', layer=IPyAMSLayer)
class HTMLPortletPreviewer(PortletPreviewer):
    """Rich text portlet previewer"""
