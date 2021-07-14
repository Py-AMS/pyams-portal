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

"""PyAMS_portal.portlets.spacer.zmi module

"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer
from pyams_portal.portlets.spacer import ISpacerPortletSettings
from pyams_portal.zmi import PortletPreviewer
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config


@adapter_config(required=(Interface, IPyAMSLayer, Interface, ISpacerPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/spacer-preview.pt', layer=IPyAMSLayer)
class SpacerPortletPreviewer(PortletPreviewer):
    """Spacer portlet previewer"""
