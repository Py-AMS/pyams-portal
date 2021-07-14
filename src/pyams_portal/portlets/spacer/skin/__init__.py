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

"""PyAMS_portal.portlets.spacer.skin module

"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortletRenderer
from pyams_portal.portlets.spacer import ISpacerPortletSettings
from pyams_portal.portlets.spacer.interfaces import ISpacerPortletRendererSettings
from pyams_portal.skin import PortletRenderer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


@factory_config(provided=ISpacerPortletRendererSettings)
class SpacerPortletRendererSettings(Persistent, Contained):
    """Spacer portlet renderer settings"""

    transparent = FieldProperty(ISpacerPortletRendererSettings['transparent'])
    background_color = FieldProperty(ISpacerPortletRendererSettings['background_color'])
    with_ruler = FieldProperty(ISpacerPortletRendererSettings['with_ruler'])


#
# Spacer portlet renderers
#

class BaseSpacerPortletRenderer(PortletRenderer):
    """Base spacer renderer"""

    settings_interface = ISpacerPortletRendererSettings


@adapter_config(required=(IPortalContext, IPyAMSLayer, Interface, ISpacerPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/spacer.pt', layer=IPyAMSLayer)
class SpacerPortletDefaultRenderer(BaseSpacerPortletRenderer):
    """Spacer portlet renderer"""

    label = _("Simple spacer (default)")
    weight = 10


@adapter_config(name='double-spacer',
                required=(IPortalContext, IPyAMSLayer, Interface, ISpacerPortletSettings),
                provides=IPortletRenderer)
@template_config(template='templates/spacer-double.pt', layer=IPyAMSLayer)
class DoubleSpacerPortletDefaultRenderer(BaseSpacerPortletRenderer):
    """Double spacer portlet renderer"""

    label = _("Double spacer")
    weight = 20
