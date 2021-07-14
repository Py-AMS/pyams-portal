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

"""PyAMS_portal.portlets.spacer.interfaces module

This module provides spacer portlet interfaces.
"""

from zope.interface import Interface
from zope.schema import Bool

from pyams_portal.interfaces import IPortletSettings
from pyams_utils.schema import ColorField


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class ISpacerPortletSettings(IPortletSettings):
    """Spacer portlet settings interface"""


class ISpacerPortletRendererSettings(Interface):
    """Spacer portlet renderer settings"""

    transparent = Bool(title=_("Transparent spacer?"),
                       description=_("If 'no', spacer background will be defined by "
                                     "selected color"),
                       required=True,
                       default=True)

    background_color = ColorField(title=_("Background color"),
                                  description=_("Color selected for background, if "
                                                "transparency is disabled"),
                                  required=False,
                                  default='fff')

    with_ruler = Bool(title=_("Horizontal ruler?"),
                      description=_("If 'yes', an horizontal ruler will be displayed in "
                                    "the middle of the spacer"),
                      required=True,
                      default=False)
