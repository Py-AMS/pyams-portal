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

"""PyAMS_portal.portlets.carousel.skin.interfaces module

"""

from zope.interface import Interface
from zope.schema import Bool, Choice, TextLine


__docformat__ = 'restructuredtext'

from pyams_file.interfaces.thumbnail import THUMBNAILERS_VOCABULARY_NAME
from pyams_portal import _  # pylint: disable=ungrouped-imports


CAROUSEL_RENDERER_SETTINGS_KEY = 'pyams_portal.renderer::carousel'


class ICarouselPortletRendererSettings(Interface):
    """Carousel portlet renderer settings interface"""

    css_class = TextLine(title=_("CSS class"),
                         description=_("Carousel container CSS class"),
                         required=False,
                         default='carousel')

    thumb_selection = Choice(title=_("Images selection"),
                             description=_("Carousel can use responsive selections, but you can "
                                           "also force selection of another specific selection"),
                             vocabulary=THUMBNAILERS_VOCABULARY_NAME,
                             required=False)

    automatic_slide = Bool(title=_("Automatic sliding"),
                           description=_("If 'no', sliding will only be activated manually"),
                           required=True,
                           default=True)

    fade_effect = Bool(title=_("Fade effect"),
                       description=_("If 'yes', slide to slide animation will use a fade effect "
                                     "instead of lateral sliding"),
                       required=True,
                       default=False)

    display_controls = Bool(title=_("Display controls"),
                            description=_("If 'yes', display arrows to navigate between slides"),
                            required=True,
                            default=False)

    display_indicators = Bool(title=_("Display indicators"),
                              description=_("If 'yes', display indicators to show position of "
                                            "current slide"),
                              required=True,
                              default=False)

    display_captions = Bool(title=_("Display captions"),
                            description=_("If 'no', slides titles and leads are not displayed"),
                            required=True,
                            default=True)

    enable_touch = Bool(title=_("Enable swiping"),
                        description=_("If 'no', touch events will be disabled on touchscreens"),
                        required=True,
                        default=True)
