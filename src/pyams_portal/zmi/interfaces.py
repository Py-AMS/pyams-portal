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

"""PyAMS_portal.zmi.interfaces module

This module defines interfaces of components used for portlets management interface.
"""

__docformat__ = 'restructuredtext'


from zope.interface import Attribute, Interface

from pyams_form.interfaces.form import IForm


class IPortletConfigurationEditor(Interface):
    """Portlet configuration editor interface"""

    settings_factory = Attribute("Editor settings factory interface")


class IPortalContextPresentationMenu(Interface):
    """Portal context presentation menu marker interface"""


class IPortalContextPresentationForm(IForm):
    """Portal context presentation form marker interface"""
