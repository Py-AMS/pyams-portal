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

"""PyAMS_portal.portlets.html module

This module defines HTML portlets, which can be used to include rich text or raw HTML
code inside a page template.
"""

from zope.schema.fieldproperty import FieldProperty

from pyams_portal.portlet import Portlet, PortletSettings, portlet_config
from pyams_portal.portlets.html.interfaces import IHTMLPortletSettings, IRawPortletSettings
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


#
# Raw HTML code portlet
#

RAW_PORTLET_NAME = 'pyams_portal.portlet.raw'


@factory_config(provided=IRawPortletSettings)
class RawPortletSettings(PortletSettings):
    """Raw HTML code portlet settings"""

    title = FieldProperty(IRawPortletSettings['title'])
    body = FieldProperty(IRawPortletSettings['body'])


@portlet_config(permission=None)
class RawPortlet(Portlet):
    """Raw HTML code portlet"""

    name = RAW_PORTLET_NAME
    label = _("Source code")

    settings_factory = IRawPortletSettings
    toolbar_css_class = 'fas fa-code'


#
# Rich text portlet
#

HTML_PORTLET_NAME = 'pyams_portal.portlet.html'


@factory_config(provided=IHTMLPortletSettings)
class HTMLPortletSettings(PortletSettings):
    """Rich text portlet settings"""

    body = FieldProperty(IHTMLPortletSettings['body'])


@portlet_config(permission=None)
class HTMLPortlet(Portlet):
    """Rich text portlet"""

    name = HTML_PORTLET_NAME
    label = _("Rich text")

    settings_factory = IHTMLPortletSettings
    toolbar_css_class = 'fas fa-font'
