#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_portal.thumbnails module

This module defines persistent classes and adapters used to handle
portlets renderers thumbnails.
"""

from persistent import Persistent
from persistent.mapping import PersistentMapping
from zope.container.contained import Contained
from zope.location import locate
from zope.location.interfaces import ISublocations
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.interfaces import ITraversable

from pyams_file.property import FileProperty
from pyams_portal.interfaces import IPortalTemplateContainer, IPortletRendererThumbnail, IPortletsRenderersThumbnails, \
    PORTLETS_RENDERERS_SETTINGS_KEY
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.factory import create_object, factory_config
from pyams_utils.interfaces.form import NOT_CHANGED, TO_BE_DELETED


@factory_config(IPortletRendererThumbnail)
class PortletRendererThumbnail(Persistent, Contained):
    """Single portlet renderer thumbnail"""

    thumbnail = FileProperty(IPortletRendererThumbnail['thumbnail'])


@factory_config(IPortletsRenderersThumbnails)
class PortletsRenderersThumbnails(Persistent, Contained):
    """Portlets renderers thumbnails persistent class"""

    _thumbnails = FieldProperty(IPortletsRenderersThumbnails['thumbnails'])

    @property
    def thumbnails(self):
        """Thumbnails getter"""
        if self._thumbnails is None:
            self._thumbnails = PersistentMapping()
            locate(self._thumbnails, self)
        return self._thumbnails

    @thumbnails.setter
    def thumbnails(self, values):
        """Thumbnails setter"""
        thumbnails = self.thumbnails
        for name, value in values.items():
            if value is NOT_CHANGED:
                continue
            if (value is TO_BE_DELETED) and name in thumbnails:
                del thumbnails[name]
            else:
                thumbnail = thumbnails.get(name)
                if IPortletRendererThumbnail.providedBy(value):
                    thumbnails[name] = value
                else:
                    if thumbnail is None:
                        thumbnail = create_object(IPortletRendererThumbnail)
                        locate(thumbnail, self.thumbnails, name)
                    thumbnail.thumbnail = value
                    thumbnails[name] = thumbnail

    def get_thumbnail(self, portlet_name, renderer_name):
        """Thumbnail image getter"""
        name = f'{portlet_name}::{renderer_name}' if renderer_name else portlet_name
        thumbnail = self.thumbnails.get(name)
        if thumbnail is not None:
            return thumbnail.thumbnail
        return None

    def set_thumbnail(self, portlet_name, renderer_name, value):
        """Thumbnail setter"""
        name = f'{portlet_name}::{renderer_name}' if renderer_name else portlet_name
        if name in self.thumbnails:
            self.thumbnails[name].thumbnail = value
        else:
            thumbnail = create_object(IPortletRendererThumbnail)
            locate(thumbnail, self.thumbnails, name)
            thumbnail.thumbnail = value
            self.thumbnails[name] = thumbnail


@adapter_config(required=IPortalTemplateContainer,
                provides=IPortletsRenderersThumbnails)
def portal_templates_container_renderers_thumbnails(context):
    """Portal templates container renderers thumbnails"""
    return get_annotation_adapter(context, PORTLETS_RENDERERS_SETTINGS_KEY,
                                  IPortletsRenderersThumbnails, name='++thumbnails++')


@adapter_config(name='thumbnails',
                required=IPortalTemplateContainer,
                provides=ISublocations)
class PortalTemplateContainerRenderersThumbnailsSublocations(ContextAdapter):
    """Portal templates container renderers thumbnails sub-locations"""

    def sublocations(self):
        """Thumbnails sub-locations getter"""
        yield IPortletsRenderersThumbnails(self.context)


@adapter_config(name='thumbnails',
                required=IPortalTemplateContainer,
                provides=ITraversable)
class PortalTemplateContainerRenderersThumbnailsTraverser(ContextAdapter):
    """Portal templates container renderers thumbnails traverser"""

    def traverse(self, name, furtherpath=None):
        return IPortletsRenderersThumbnails(self.context, None).thumbnails
