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

"""PyAMS_portal.portlet module

This module defines all portlet-related components.
"""

__docformat__ = 'restructuredtext'

import logging

import venusian
from persistent import Persistent
from persistent.mapping import PersistentMapping
from pyramid.exceptions import ConfigurationError
from zope.container.contained import Contained
from zope.copy import clone
from zope.interface import alsoProvides, implementer, noLongerProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable

from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalPortletsConfiguration, \
    IPortalTemplate, IPortlet, IPortletConfiguration, IPortletRenderer, \
    IPortletSettings, MANAGE_TEMPLATE_PERMISSION, PORTLETS_VOCABULARY_NAME
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config, get_object_factory, is_interface
from pyams_utils.registry import get_pyramid_registry
from pyams_utils.request import check_request
from pyams_utils.vocabulary import vocabulary_config


LOGGER = logging.getLogger('PyAMS (portal)')


@implementer(IPortlet)
class Portlet:
    """Base portlet utility"""

    permission = FieldProperty(IPortlet['permission'])

    toolbar_image = None
    toolbar_css_class = 'fa-edit'

    settings_factory = None


class portlet_config:  # pylint: disable=invalid-name
    """Class decorator used to declare a portlet"""

    venusian = venusian  # for testing injection

    def __init__(self, **settings):
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):  # pylint: disable=invalid-name,unused-argument
            name = settings.get('name') or getattr(ob, 'name', name)
            if name is None:
                raise ConfigurationError("You must provide a name for a portlet")

            permission = settings.get('permission')
            if permission is not None:
                ob.permission = permission

            if type(ob) is type:  # pylint: disable=unidiomatic-typecheck
                factory = ob
                component = None
            else:
                factory = None
                component = ob

            LOGGER.debug("Registering portlet {0} named '{1}'".format(
                str(component) if component else str(factory), name))
            config = context.config.with_package(info.module)  # pylint: disable=no-member
            registry = settings.get('registry', config.registry)
            registry.registerUtility(component=component, factory=factory,
                                     provided=IPortlet, name=name)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)
        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped


@vocabulary_config(name=PORTLETS_VOCABULARY_NAME)
class PortletVocabulary(SimpleVocabulary):
    """Portlet vocabulary"""

    def __init__(self, context):  # pylint: disable=unused-argument
        request = check_request()
        translate = request.localizer.translate
        utils = request.registry.getUtilitiesFor(IPortlet)
        terms = [
            SimpleTerm(name, title=translate(util.label))
            for name, util in sorted(utils, key=lambda x: translate(x[1].label))
        ]
        super().__init__(terms)


#
# Portlet configuration
#

@implementer(IPortletSettings)
class PortletSettings(Persistent, Contained):
    """Portlet settings persistent class

    This class is supposed to be sub-classed by all custom portlet subclasses to
    store their configuration settings.

    Each portlet sub-class must define it's settings factory in it's "settings_factory" attribute.
    Given factory can be a function, a class or an interface; in this last case, implementation
    is looking for default object factory registered for this interface.
    """

    _renderer = FieldProperty(IPortletSettings['renderer'])

    __name__ = '++settings++'

    def __init__(self, configuration=None):
        self.__parent__ = configuration

    @property
    def visible(self):
        """Visibility getter"""
        return self._renderer != 'hidden'

    @property
    def renderer(self):
        """Renderer name getter"""
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        """Renderer setter"""
        value = value or ''
        if value == self._renderer:
            return
        request = check_request()
        registry = request.registry
        renderer = registry.queryMultiAdapter((request.root, request, request, self),
                                              IPortletRenderer, name=self._renderer)
        if (renderer is not None) and (renderer.target_interface is not None):
            noLongerProvides(self, renderer.target_interface)
        self._renderer = value
        renderer = registry.queryMultiAdapter((request.root, request, request, self),
                                              IPortletRenderer, name=self._renderer)
        if (renderer is not None) and (renderer.target_interface is not None):
            alsoProvides(self, renderer.target_interface)

    def get_renderer(self, request=None):
        """Renderer adapter getter"""
        if request is None:
            request = check_request()
        return request.registry.queryMultiAdapter((request.root, request, request, self),
                                                  IPortletRenderer, name=self._renderer)

    @property
    def configuration(self):
        """Configuration getter"""
        return self.__parent__

    @configuration.setter
    def configuration(self, value):
        """Configuration setter"""
        if self.__parent__ is None:
            self.__parent__ = value


@adapter_config(required=IPortletSettings, provides=IViewContextPermissionChecker)
class PortletSettingsPermissionChecker(ContextAdapter):
    """Portlet settings permission checker"""

    edit_permission = MANAGE_TEMPLATE_PERMISSION


@factory_config(IPortletConfiguration)
class PortletConfiguration(Persistent, Contained):
    """Portlet configuration persistent class

    This class is a generic persistent class which is used to store all portlet
    configuration and is *not* supposed to be sub-classed.

    PortletConfiguration.__parent__ points to context where configuration is applied
    (each context or local template).
    PortletConfiguration.parent points to context from where configuration is inherited.
    """

    portlet_id = FieldProperty(IPortletConfiguration['portlet_id'])
    portlet_name = None
    _inherit_parent = FieldProperty(IPortletConfiguration['inherit_parent'])
    _settings = FieldProperty(IPortletConfiguration['settings'])

    def __init__(self, portlet):
        self.portlet_name = portlet.name
        factory = portlet.settings_factory
        if is_interface(factory):
            factory = get_object_factory(factory)
        assert factory is not None, "Missing portlet settings factory"
        settings = factory()
        settings.configuration = self
        self._settings = settings

    def get_portlet(self):
        """Portlet utility getter"""
        return get_pyramid_registry().queryUtility(IPortlet, name=self.portlet_name)

    @property
    def can_inherit(self):
        """Check if configuration can be inherited"""
        return not IPortalTemplate.providedBy(self.__parent__)

    @property
    def inherit_parent(self):
        """Check if inheritance is enabled"""
        return self._inherit_parent if self.can_inherit else False

    @inherit_parent.setter
    def inherit_parent(self, value):
        """Inheritance setter"""
        if (not value) or self.can_inherit:
            self._inherit_parent = value

    @property
    def override_parent(self):
        """Parent overriding getter"""
        return not self.inherit_parent

    @override_parent.setter
    def override_parent(self, value):
        """Parent overriding setter"""
        self.inherit_parent = not value

    @property
    def parent(self):
        """Parent getter"""
        parent = self.__parent__
        if IPortalTemplate.providedBy(parent):
            return parent
        while True:
            if IPortalContext.providedBy(parent):
                configuration = IPortalPortletsConfiguration(parent).get_portlet_configuration(
                    self.portlet_id)
                if not configuration.inherit_parent:
                    return parent
                page = IPortalPage(parent)
                if not page.inherit_parent:
                    break
            parent = parent.__parent__
            if parent is None:
                break
        page = IPortalPage(parent, None)
        if page is not None:
            return page.template
        return None

    @property
    def settings(self):
        """Current settings getter (using inheritance settings)"""
        if self.inherit_parent:
            return IPortalPortletsConfiguration(self.parent).get_portlet_configuration(
                self.portlet_id).settings
        return self._settings

    @property
    def editor_settings(self):
        """Editor settings getter (always return local settings)"""
        return self._settings

    def get_settings(self, allow_inherit=True):
        """Settings getter (using inheritance or not according to allow_inherit argument)"""
        if allow_inherit:
            return self.settings
        return self._settings


@adapter_config(required=IPortlet, provides=IPortletConfiguration)
def portlet_configuration_adapter(portlet):
    """Portlet configuration factory"""
    return PortletConfiguration(portlet)


@adapter_config(required=IPortletConfiguration, provides=IPortletSettings)
def portlet_configuration_settings_adapter(configuration):
    """Portlet configuration settings adapter"""
    return configuration.settings


@adapter_config(required=IPortletSettings, provides=IPortletConfiguration)
def portlet_settings_configuration_adapter(settings):
    """Portlet settings configuration adapter"""
    return settings.configuration


@adapter_config(name='settings',
                required=IPortletConfiguration, provides=ITraversable)
class PortletConfigurationSettingsTraverser(ContextAdapter):
    """++settings++ portlet configuration traverser"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Portlet configuration traverser to settings"""
        return self.context.settings


@adapter_config(required=IPortletConfiguration, provides=IViewContextPermissionChecker)
class PortletConfigurationPermissionChecker(ContextAdapter):
    """Portlet configuration permission checker"""

    edit_permission = MANAGE_TEMPLATE_PERMISSION


#
# Template portlets configuration
#

@factory_config(IPortalPortletsConfiguration)
class PortalPortletsConfiguration(PersistentMapping, Contained):
    """Portal portlets configuration"""

    @classmethod
    def clone(cls, source_config, new_parent):
        """Clone source configuration"""
        configuration = source_config.__class__()
        get_pyramid_registry().notify(ObjectCreatedEvent(configuration))
        locate(configuration, new_parent)
        for config_id, config_portlet in source_config.items():
            config = clone(config_portlet)
            configuration[config_id] = config
        return configuration

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        locate(value, self.__parent__, '++portlet++{0}'.format(key))

    def get_portlet_configuration(self, portlet_id):
        """Portlet configuration getter"""
        configuration = self.get(portlet_id)
        if configuration is None:
            if IPortalTemplate.providedBy(self.__parent__):
                portlets = IPortalPortletsConfiguration(self.__parent__)
            else:
                template = IPortalPage(self.__parent__).template
                portlets = IPortalPortletsConfiguration(template)
            configuration = clone(portlets.get_portlet_configuration(portlet_id))
            get_pyramid_registry().notify(ObjectCreatedEvent(configuration))
            self.set_portlet_configuration(portlet_id, configuration)
        return configuration

    def set_portlet_configuration(self, portlet_id, config):
        """Portlet configuration setter"""
        config.portlet_id = portlet_id
        self[portlet_id] = config

    def delete_portlet_configuration(self, portlet_id):
        """Delete portlet configuration"""
        if isinstance(portlet_id, int):
            portlet_id = (portlet_id,)
        for p_id in portlet_id:
            del self[p_id]
