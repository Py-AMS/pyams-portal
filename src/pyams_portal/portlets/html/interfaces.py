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

"""PyAMS_portal.portlets.html.interfaces module

This module defines interfaces of HTML portlet.
"""

from pyams_i18n.schema import I18nHTMLField, I18nTextField, I18nTextLineField
from pyams_portal.interfaces import IPortletSettings

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class IRawPortletSettings(IPortletSettings):
    """Raw HTML code portlet settings interface"""

    title = I18nTextLineField(title=_("Title"),
                              required=False)

    body = I18nTextField(title=_("Source code"),
                         description=_("This code will be used 'as is', without any "
                                       "transformation, if using the 'raw' renderer. Use with "
                                       "care!!<br />"
                                       "You can enter &lt;CTRL&gt;+&lt;,&gt; to display text "
                                       "editor options..."),
                         required=False)


class IHTMLPortletSettings(IPortletSettings):
    """Rich text portlet settings interface"""

    body = I18nHTMLField(title=_("Body"),
                         required=False)
