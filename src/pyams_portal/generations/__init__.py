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

"""PyAMS_portal.generations module

This module provides site generation utility to automatically create
a shared templates container.
"""

from pyams_portal.interfaces import IPortalTemplateContainer
from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_utils.registry import utility_config

__docformat__ = 'restructuredtext'


REQUIRED_UTILITIES = ((IPortalTemplateContainer, '', None, 'Templates container'),)


@utility_config(name='PyAMS portal', provides=ISiteGenerations)
class PortalGenerationsChecker:
    """Portal package generations checker"""

    order = 100
    generation = 1

    def evolve(self, site, current=None):  # pylint: disable=no-self-use,unused-argument
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)
