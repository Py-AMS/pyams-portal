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

"""PyAMS_portal.generations.evolve1 module

This upgrade module is updating portal context annotations to move portlets
configuration from context to portal page.
"""

import logging

from zope.annotation.interfaces import IAnnotations
from zope.component.interfaces import ISite

from pyams_portal.interfaces import IPortalContext, IPortalPage, PORTLETS_CONFIGURATION_KEY
from pyams_utils.container import find_objects_providing
from pyams_utils.registry import get_local_registry, set_local_registry


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (portal)')


def evolve(site: ISite):
    """Evolve 1: update portal page annotations"""
    registry = get_local_registry()
    try:
        set_local_registry(site.getSiteManager())
        for context in find_objects_providing(site, IPortalContext):
            context_annotations = IAnnotations(context)
            if PORTLETS_CONFIGURATION_KEY in context_annotations:
                page = IPortalPage(context, None)
                if page is not None:
                    LOGGER.info(f"Updating portlets annotations for {context!r}")
                    page_annotations = IAnnotations(page)
                    page_annotations[PORTLETS_CONFIGURATION_KEY] = \
                        context_annotations[PORTLETS_CONFIGURATION_KEY]
                    del context_annotations[PORTLETS_CONFIGURATION_KEY]
    finally:
        set_local_registry(registry)
