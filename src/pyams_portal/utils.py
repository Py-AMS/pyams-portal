#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_portal.utils module

This module is used to provide custom utility functions.
"""

from zope.interface.interfaces import ComponentLookupError

from pyams_portal.interfaces import IPortalPage, IPortalTemplate
from pyams_utils.registry import get_pyramid_registry


__docformat__ = 'restructuredtext'


MARKER = object()


def get_portal_page(context, page_name='', default=MARKER):
    """Portal page getter"""
    if IPortalTemplate.providedBy(context) or IPortalPage.providedBy(context):  # pylint: disable=no-value-for-parameter
        return context
    registry = get_pyramid_registry()
    adapter = registry.queryAdapter(context, IPortalPage, name=page_name)
    if adapter is None:
        if default is not MARKER:
            return default
        raise ComponentLookupError()
    return adapter
