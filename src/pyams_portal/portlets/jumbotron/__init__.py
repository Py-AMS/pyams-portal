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

"""PyAMS_portal.portlets.jumbotron module


"""

from zope.schema.fieldproperty import FieldProperty

from pyams_portal.portlet import Portlet, PortletSettings, portlet_config
from pyams_portal.portlets.jumbotron.interfaces import IJumbotronPortletSettings
from pyams_sequence.reference import InternalReferenceMixin
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


JUMBOTRON_PORTLET_NAME = 'pyams_portal.portlet.jumbotron'


@factory_config(provided=IJumbotronPortletSettings)
class JumbotronPortletSettings(InternalReferenceMixin, PortletSettings):
    """Jumbotron portlet settings"""

    title = FieldProperty(IJumbotronPortletSettings['title'])
    lead = FieldProperty(IJumbotronPortletSettings['lead'])
    display_ruler = FieldProperty(IJumbotronPortletSettings['display_ruler'])
    body = FieldProperty(IJumbotronPortletSettings['body'])
    reference = FieldProperty(IJumbotronPortletSettings['reference'])
    target_url = FieldProperty(IJumbotronPortletSettings['target_url'])
    button_label = FieldProperty(IJumbotronPortletSettings['button_label'])
    button_status = FieldProperty(IJumbotronPortletSettings['button_status'])


@portlet_config(permission=None)
class JumbotronPortlet(Portlet):
    """Jumbotron portlet"""

    name = JUMBOTRON_PORTLET_NAME
    label = _("Bootstrap: Jumbotron")

    settings_factory = IJumbotronPortletSettings
    toolbar_css_class = 'far fa-newspaper'
