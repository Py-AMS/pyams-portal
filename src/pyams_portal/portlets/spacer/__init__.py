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

"""PyAMS_portal.portlets.spacer module

Spacer portlet module components.
"""

from pyams_portal.portlet import Portlet, PortletSettings, portlet_config
from pyams_portal.portlets.spacer.interfaces import ISpacerPortletSettings
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


SPACER_PORTLET_NAME = 'pyams_portal.portlet.spacer'


@factory_config(provided=ISpacerPortletSettings)
class SpacerPortletSettings(PortletSettings):
    """Spacer portlet settings"""


@portlet_config(permission=None)
class SpacerPortlet(Portlet):
    """Spacer portlet"""

    name = SPACER_PORTLET_NAME
    label = _("Spacer")

    settings_factory = ISpacerPortletSettings
    toolbar_css_class = 'far fa-window-minimize'
