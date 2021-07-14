#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS portal.include module

This module is used for Pyramid integration.
"""

import re

from zope.interface import classImplements

from pyams_portal.interfaces import DESIGNER_ROLE, IPortalContext, MANAGE_TEMPLATE_PERMISSION
from pyams_security.interfaces import ADMIN_USER_ID, SYSTEM_ADMIN_ROLE
from pyams_security.interfaces.base import PUBLIC_PERMISSION, ROLE_ID, VIEW_PERMISSION, \
    VIEW_SYSTEM_PERMISSION
from pyams_site.site import BaseSiteRoot


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_portal:locales')

    # register permissions
    config.register_permission({
        'id': MANAGE_TEMPLATE_PERMISSION,
        'title': _("Manage presentation templates")
    })

    # register roles
    config.register_role({
        'id': DESIGNER_ROLE,
        'title': _("Designer (role)"),
        'permissions': {
            PUBLIC_PERMISSION, VIEW_PERMISSION, VIEW_SYSTEM_PERMISSION,
            MANAGE_TEMPLATE_PERMISSION
        },
        'managers': {
            ADMIN_USER_ID,
            ROLE_ID.format(SYSTEM_ADMIN_ROLE)
        }
    })

    # add portal support to site root
    classImplements(BaseSiteRoot, IPortalContext)

    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        config.scan(ignore=[re.compile(r'pyams_portal\..*\.zmi\.?.*').search])
    else:
        config.scan()
