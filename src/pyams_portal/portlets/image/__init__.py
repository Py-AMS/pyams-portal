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

"""PyAMS_portal.portlets.image module

This module defines a basic image portlet.
"""

from zope.interface import alsoProvides

from pyams_file.interfaces import IImageFile, IResponsiveImage
from pyams_file.property import FileProperty
from pyams_portal.portlet import Portlet, PortletSettings, portlet_config
from pyams_portal.portlets.image.interfaces import IImagePortletSettings
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports  # pylint: disable=ungrouped-imports


IMAGE_PORTLET_NAME = 'pyams_portal.portlet.image'


@factory_config(provided=IImagePortletSettings)
class ImagePortletSettings(PortletSettings):
    """Image portlet settings"""

    _image = FileProperty(IImagePortletSettings['image'])

    @property
    def image(self):
        """Image getter"""
        return self._image

    @image.setter
    def image(self, value):
        """Image setter"""
        self._image = value
        if IImageFile.providedBy(self._image):
            alsoProvides(self._image, IResponsiveImage)


@portlet_config(permission=None)
class ImagePortlet(Portlet):
    """Image portlet"""

    name = IMAGE_PORTLET_NAME
    label = _("Image")

    settings_factory = IImagePortletSettings
    toolbar_css_class = 'far fa-image'
