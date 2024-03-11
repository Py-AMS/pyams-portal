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

"""PyAMS_portal.portlets.cards.skin.interfaces module

"""

from zope.interface import Interface
from zope.schema import TextLine

from pyams_skin.schema import BootstrapThumbnailsSelectionField

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class ICardsPortletRendererSettings(Interface):
    """Cards portlet renderer settings interface"""

    css_class = TextLine(title=_("CSS class"),
                         description=_("Cards container CSS class"),
                         default='row row-cols-2 row-cols-md-3 row-cols-lg-4')

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Images selection"),
        description=_("Cards will use responsive selections by default, "
                      "but you can also force selection of another "
                      "specific selection"),
        default_selection='pano',
        change_selection=True,
        default_width=12,
        change_width=False,
        required=False)


class ICardsPortletMasonryRendererSettings(Interface):
    """Cards portlet Masonry renderer settings interface"""

    css_class = TextLine(title=_("CSS class"),
                         description=_("Cards container CSS class"),
                         default='card-columns')

    thumb_selection = BootstrapThumbnailsSelectionField(
        title=_("Images selection"),
        description=_("Cards will use responsive selections by default, "
                      "but you can also force selection of another "
                      "specific selection"),
        default_selection='pano',
        change_selection=True,
        default_width=12,
        change_width=False,
        required=False)
