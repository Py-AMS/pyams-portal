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

"""PyAMS_portal.portlets.carousel.skin module

This module provides renderers for carousel portlet.
"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.portlets.carousel.interfaces import ICarouselPortletSettings
from pyams_portal.portlets.carousel.skin.interfaces import CAROUSEL_RENDERER_SETTINGS_KEY, \
    ICarouselPortletRendererSettings
from pyams_portal.skin import PortletRenderer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


@factory_config(provided=ICarouselPortletRendererSettings)
class CarouselPortletRendererSettings(Persistent, Contained):
    """Carousel portlet renderer settings"""

    css_class = FieldProperty(ICarouselPortletRendererSettings['css_class'])
    thumb_selection = FieldProperty(ICarouselPortletRendererSettings['thumb_selection'])
    automatic_slide = FieldProperty(ICarouselPortletRendererSettings['automatic_slide'])
    fade_effect = FieldProperty(ICarouselPortletRendererSettings['fade_effect'])
    display_controls = FieldProperty(ICarouselPortletRendererSettings['display_controls'])
    display_indicators = FieldProperty(ICarouselPortletRendererSettings['display_indicators'])
    display_captions = FieldProperty(ICarouselPortletRendererSettings['display_captions'])
    enable_touch = FieldProperty(ICarouselPortletRendererSettings['enable_touch'])


@adapter_config(required=ICarouselPortletSettings,
                provides=ICarouselPortletRendererSettings)
def carousel_portlet_renderer_settings(context):
    """Carousel portlet renderer settings"""
    return get_annotation_adapter(context, CAROUSEL_RENDERER_SETTINGS_KEY,
                                  ICarouselPortletRendererSettings)


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, ICarouselPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/carousel.pt', layer=IPyAMSLayer)
class CarouselPortletRenderer(PortletRenderer):
    """Carousel portlet renderer"""

    label = _("Bootstrap carousel renderer (default)")
    weight = 1

    settings_interface = ICarouselPortletRendererSettings
