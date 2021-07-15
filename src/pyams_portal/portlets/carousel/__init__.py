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

"""PyAMS_portal.portrlets.carousel module

"""

from persistent import Persistent
from zope.container.contained import Contained
from zope.container.ordered import OrderedContainer
from zope.interface import Interface, alsoProvides
from zope.schema.fieldproperty import FieldProperty

from pyams_file.interfaces import IImageFile, IResponsiveImage
from pyams_file.property import FileProperty
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import MANAGE_TEMPLATE_PERMISSION
from pyams_portal.portlet import Portlet, PortletSettings, portlet_config
from pyams_portal.portlets.carousel.interfaces import ICarouselImage, ICarouselPortletSettings
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.container import SimpleContainerMixin
from pyams_utils.factory import factory_config
from pyams_zmi.interfaces import IObjectLabel


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


CAROUSEL_PORTLET_NAME = 'pyams_portal.portlet.carousel'


@factory_config(provided=ICarouselImage)
class CarouselImage(Persistent, Contained):
    """Carousel image"""

    visible = FieldProperty(ICarouselImage['visible'])
    title = FieldProperty(ICarouselImage['title'])
    lead = FieldProperty(ICarouselImage['lead'])
    _illustration = FileProperty(ICarouselImage['illustration'])
    interval = FieldProperty(ICarouselImage['interval'])

    @property
    def illustration(self):
        """Illustration getter"""
        return self._illustration

    @illustration.setter
    def illustration(self, value):
        """Illustration setter"""
        self._illustration = value
        if IImageFile.providedBy(self._illustration):
            alsoProvides(self._illustration, IResponsiveImage)

    @illustration.deleter
    def illustration(self):
        """Illustration deleter"""
        del self._illustration


@adapter_config(required=(ICarouselImage, IPyAMSLayer, Interface),
                provides=IObjectLabel)
def carousel_image_label(context, request, view):  # pylint: disable=unused-argument
    """Carousel image label getter"""
    return II18n(context).query_attribute('title', request=request)


@adapter_config(required=ICarouselImage, provides=IViewContextPermissionChecker)
class CarouselImagePermissionChecker(ContextAdapter):
    """Carousel image permission checker"""

    edit_permission = MANAGE_TEMPLATE_PERMISSION


@factory_config(provided=ICarouselPortletSettings)
class CarouselPortletSettings(SimpleContainerMixin, OrderedContainer, PortletSettings):
    """Carousel portlet settings"""

    title = FieldProperty(ICarouselPortletSettings['title'])

    def get_visible_items(self):
        """Visible items getter"""
        yield from filter(lambda x: x.visible, self.values())


@portlet_config(permission=None)
class CarouselPortlet(Portlet):
    """Carousel portlet"""

    name = CAROUSEL_PORTLET_NAME
    label = _("Bootstrap: carousel")

    settings_factory = ICarouselPortletSettings
    toolbar_css_class = 'far fa-images'
