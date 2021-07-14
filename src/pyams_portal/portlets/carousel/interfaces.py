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

"""PyAMS_portal.portlets.carousel.interfaces module

"""

__docformat__ = 'restructuredtext'

from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.location.interfaces import IContained
from zope.schema import Bool, Int

from pyams_file.schema import ImageField
from pyams_i18n.schema import I18nTextLineField
from pyams_portal import _  # pylint: disable=ungrouped-imports
from pyams_portal.interfaces import IPortletSettings


class ICarouselItem(IContained):
    """Carousel item interface"""

    visible = Bool(title=_("Visible item?"),
                   required=True,
                   default=True)


class ICarouselImage(ICarouselItem):
    """Carousel image interface"""

    title = I18nTextLineField(title=_("Title"),
                              description=_("Image title"),
                              required=False)

    lead = I18nTextLineField(title=_("Leading text"),
                             description=_("Show text to be displayed below title"),
                             required=False)

    illustration = ImageField(title=_("Illustration"),
                              description=_("Carousel image illustration"),
                              required=False)

    interval = Int(title=_("Image interval"),
                   description=_("Image slide duration, in seconds"),
                   default=5)


class ICarouselPortletSettings(IPortletSettings, IContainer):
    """Carousel portlet settings interface"""

    contains(ICarouselItem)

    title = I18nTextLineField(title=_("Title"),
                              description=_("Main component title"),
                              required=False)

    def get_visible_items(self):
        """Get iterator over visible items"""
