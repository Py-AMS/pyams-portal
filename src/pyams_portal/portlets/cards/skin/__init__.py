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

"""PyAMS_portal.portlets.cards.skin module

This module provides renderers for cards portlet.
"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.portlets.cards import ICardsPortletSettings
from pyams_portal.portlets.cards.skin.interfaces import CARDS_RENDERER_SETTINGS_KEY, \
    ICardsPortletMasonryRendererSettings, ICardsPortletRendererSettings
from pyams_portal.skin import PortletRenderer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


#
# Cards default renderer
#

@factory_config(provided=ICardsPortletRendererSettings)
class CardsPortletRendererSettings(Persistent, Contained):
    """Cards portlet renderer settings"""

    css_class = FieldProperty(ICardsPortletRendererSettings['css_class'])
    thumb_selection = FieldProperty(ICardsPortletRendererSettings['thumb_selection'])


@adapter_config(required=ICardsPortletSettings,
                provides=ICardsPortletRendererSettings)
def cards_portlet_renderer_settings(context):
    """Cards portlet renderer settings"""
    return get_annotation_adapter(context, CARDS_RENDERER_SETTINGS_KEY,
                                  ICardsPortletRendererSettings)


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, ICardsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/cards.pt', layer=IPyAMSLayer)
class CardsPortletRenderer(PortletRenderer):
    """Cards portlet renderer"""

    label = _("Bootstrap cards renderer (default)")
    weight = 1

    settings_interface = ICardsPortletRendererSettings


#
# Cards Masonry" renderer
#

@factory_config(provided=ICardsPortletMasonryRendererSettings)
class CardsPortletMasonryRendererSettings(Persistent, Contained):
    """Cards portlet Masonry renderer settings"""

    css_class = FieldProperty(ICardsPortletMasonryRendererSettings['css_class'])
    thumb_selection = FieldProperty(ICardsPortletMasonryRendererSettings['thumb_selection'])


@adapter_config(required=ICardsPortletSettings,
                provides=ICardsPortletMasonryRendererSettings)
def cards_portlet_masonry_renderer_settings(context):
    """Cards portlet Masonry renderer settings"""
    return get_annotation_adapter(context, CARDS_RENDERER_SETTINGS_KEY,
                                  ICardsPortletMasonryRendererSettings)


@adapter_config(name='cards::masonry',
                required=(IPortalContext, IPyAMSLayer, Interface, ICardsPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/cards-masonry.pt', layer=IPyAMSLayer)
class CardsPortletMasonryRenderer(PortletRenderer):
    """Cards portlet Masonry renderer"""

    label = _("Bootstrap cards Masonry renderer")
    weight = 10

    settings_interface = ICardsPortletMasonryRendererSettings
