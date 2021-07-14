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

"""PyAMS_portal.portlets.image.skin module

This module provides renderers for image portlet.
"""

from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.portlets.image import IImagePortletSettings
from pyams_portal.skin import PortletRenderer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports  # pylint: disable=ungrouped-imports


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, IImagePortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/image.pt', layer=IPyAMSLayer)
class ImagePortletRenderer(PortletRenderer):
    """Image portlet renderer"""

    label = _("Image renderer (default)")
    weight = 1
