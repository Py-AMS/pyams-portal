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

"""PyAMS_portal.skin main module

This modules defines the main portlets rendering components.
"""

from zope.interface import Interface, implementer
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable

from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalTemplateConfiguration, \
    IPortlet, IPortletRenderer, IPortletRendererSettings, IPortletSettings, \
    PORTLET_RENDERERS_VOCABULARY, PORTLET_RENDERER_SETTINGS_KEY, PREVIEW_MODE
from pyams_portal.portlet import LOGGER
from pyams_utils.adapter import ContextAdapter, adapter_config, get_adapter_weight, \
    get_annotation_adapter
from pyams_utils.cache import get_cache
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.request import check_request, get_annotations, get_display_context
from pyams_utils.vocabulary import vocabulary_config
from pyams_viewlet.viewlet import ViewContentProvider


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


PORTLETS_CACHE_NAME = 'portlets'
PORTLETS_CACHE_REGION = 'portlets'
PORTLETS_CACHE_NAMESPACE = 'PyAMS::portlet'
PORTLETS_CACHE_KEY = 'portlet::{hostname}::{portlet}::{context}::{lang}'
PORTLETS_CACHE_DISPLAY_CONTEXT_KEY = 'portlet::{hostname}::{portlet}:' \
                                     ':{context}::{display}::{lang}'


class PortletContentProvider(ViewContentProvider):
    """Base portlet content provider"""

    def __init__(self, context, request, view, settings):
        super().__init__(context, request, view)
        self.portlet = request.registry.queryUtility(IPortlet,
                                                     name=settings.configuration.portlet_name)
        self.settings = settings

    @property
    def renderer_settings(self):
        """Renderer settings getter"""
        return IPortletRendererSettings(self.settings, None)

    def render(self, template_name=''):
        """Render portlet content"""
        if self.portlet is None:
            return ''
        if self.portlet.permission and \
                not self.request.has_permission(self.portlet.permission, context=self.context):
            return ''
        return super().render(template_name)


@implementer(IPortletRenderer)
class PortletRenderer(PortletContentProvider):
    """Portlet renderer adapter"""

    settings_interface = None

    @property
    def settings_key(self):
        """Settings annotation key getter"""
        return PORTLET_RENDERER_SETTINGS_KEY.format(self.settings.renderer)

    target_interface = None
    use_authentication = False

    weight = 0

    @property
    def slot_configuration(self):
        """Slot configuration getter"""
        template = IPortalPage(self.context).template
        config = IPortalTemplateConfiguration(template)
        _slot_id, slot_name = config.get_portlet_slot(self.settings.configuration.portlet_id)
        return config.get_slot_configuration(slot_name)

    @property
    def use_portlets_cache(self):
        """Cache usage flag getter"""
        return not bool(self.request.params)

    def get_cache_key(self):
        """Cache key getter"""
        display_context = get_display_context(self.request)
        if display_context is None:
            return PORTLETS_CACHE_KEY.format(hostname=self.request.host,
                                             portlet=ICacheKeyValue(self.settings),
                                             context=ICacheKeyValue(self.context),
                                             lang=self.request.locale_name)
        return PORTLETS_CACHE_DISPLAY_CONTEXT_KEY.format(hostname=self.request.host,
                                                         portlet=ICacheKeyValue(self.settings),
                                                         context=ICacheKeyValue(self.context),
                                                         display=ICacheKeyValue(display_context),
                                                         lang=self.request.locale_name)

    def render(self, template_name=''):
        """Render portlet content"""
        preview_mode = get_annotations(self.request).get(PREVIEW_MODE, False)
        if preview_mode or not self.use_portlets_cache:
            return super().render(template_name)
        portlets_cache = get_cache(PORTLETS_CACHE_NAME, PORTLETS_CACHE_REGION,
                                   PORTLETS_CACHE_NAMESPACE)
        cache_key = self.get_cache_key()
        if template_name:
            cache_key = '{}::{}'.format(cache_key, template_name)
        if self.use_authentication:
            cache_key = '{}::{}'.format(cache_key, self.request.principal.id)
        # load rendered content from cache, or create output and store it in cache
        try:
            result = portlets_cache.get_value(cache_key)
            LOGGER.debug("Retrieving portlet content from cache key {0}".format(cache_key))
        except KeyError:
            self.update()
            result = super().render(template_name)
            portlets_cache.set_value(cache_key, result)
            LOGGER.debug("Storing portlet content to cache key {0}".format(cache_key))
        return result


@vocabulary_config(name=PORTLET_RENDERERS_VOCABULARY)
class PortletRenderersVocabulary(SimpleVocabulary):
    """Portlet renderers vocabulary"""

    def __init__(self, context):
        request = check_request()
        translate = request.localizer.translate
        terms = [
            SimpleTerm(name, title=translate(adapter.label))
            for name, adapter in sorted(request.registry.getAdapters((request.root, request,
                                                                      request, context),
                                                                     IPortletRenderer),
                                        key=get_adapter_weight)
        ]
        super().__init__(terms)


@adapter_config(required=IPortletSettings, provides=IPortletRendererSettings)
def portlet_renderer_settings_adapter(context):
    """Portlet renderer settings adapter"""
    renderer = context.get_renderer()
    if not renderer.settings_interface:
        return None
    return get_annotation_adapter(context, renderer.settings_key, renderer.settings_interface,
                                  name='++renderer++')


@adapter_config(name='renderer',
                required=IPortletSettings, provides=ITraversable)
class PortletSettingsRendererSettingsTraverser(ContextAdapter):
    """Portlet settings traverser to renderer settings"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Traverse settings to renderer settings"""
        return IPortletRendererSettings(self.context)


#
# Common renderers
#

@adapter_config(name='hidden',
                context=(IPortalContext, IPyAMSLayer, Interface, IPortletSettings),
                provides=IPortletRenderer)
class HiddenPortletRenderer(PortletRenderer):
    """Hidden portlet renderer"""

    label = _("Hidden portlet")
    weight = 9999

    def render(self, template_name=''):
        return ''
