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

"""PyAMS_portal.portlets.html.skin.interfaces module

This module defines portlets renderers settings interfaces.
"""

from zope.schema import Bool, Choice

from pyams_portal.interfaces import IPortletRendererSettings
from pyams_skin.interfaces import BOOTSTRAP_STATUS_VOCABULARY

__docformat__ = 'restructuredtext'

from pyams_portal import _


class IHTMLPortletAlertRendererSettings(IPortletRendererSettings):
    """HTML portlet alert renderer settings interface"""

    status = Choice(title=_("Alert status"),
                    description=_("Bootstrap alert status defines alert rendering color"),
                    required=True,
                    vocabulary=BOOTSTRAP_STATUS_VOCABULARY,
                    default='info')

    display_dismiss_button = Bool(title=_("Display dismiss button"),
                                  description=_("Select this option to display a dismiss button"),
                                  required=True,
                                  default=False)
