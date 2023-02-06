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

"""PyAMS_portal.page module

This module is used to handle portal pages. A page is the highest configuration level,
which defines the selected template for a given context.
"""

from persistent import Persistent
from pyramid.httpexceptions import HTTPBadRequest
from zope.container.contained import Contained
from zope.copy import clone
from zope.interface import alsoProvides, noLongerProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.interfaces import ITraversable

from pyams_portal.interfaces import ILocalTemplateHandler, IPortalContext, IPortalFooterContext, \
    IPortalHeaderContext, IPortalPage, IPortalPortletsConfiguration, IPortalTemplate, \
    IPortalTemplateConfiguration, LOCAL_TEMPLATE_NAME, PORTAL_PAGE_KEY, PORTLETS_CONFIGURATION_KEY
from pyams_portal.portlet import PortalPortletsConfiguration
from pyams_portal.utils import get_portal_page
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config, get_object_factory
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import get_pyramid_registry, query_utility
from pyams_utils.zodb import volatile_property


__docformat__ = 'restructuredtext'


def check_local_template(context, page_name=''):
    """Check for local template in portal context"""
    if IPortalContext.providedBy(context):  # pylint: disable=no-value-for-parameter
        page = get_portal_page(context, page_name=page_name)
        if not page.use_local_template:
            raise HTTPBadRequest("Action can be done only on local templates!")


@factory_config(IPortalPage)
class PortalPage(Persistent, Contained):
    """Portal page persistent class

    The page is the highest configuration level.
    It defines which template is used (a shared or local one), which gives
    the rows, slots and portlets lists.
    """

    name = ''

    _inherit_parent = FieldProperty(IPortalPage['inherit_parent'])
    _use_local_template = FieldProperty(IPortalPage['use_local_template'])
    _local_template = FieldProperty(IPortalPage['local_template'])
    _shared_template = FieldProperty(IPortalPage['shared_template'])

    @volatile_property
    def can_inherit(self):
        """Inherit check property getter"""
        return IPortalContext.providedBy(self.__parent__.__parent__)

    @property
    def inherit_parent(self):
        """Inheritance getter"""
        return self._inherit_parent if self.can_inherit else False  # pylint: disable=using-constant-test

    @inherit_parent.setter
    def inherit_parent(self, value):
        """Inheritance setter"""
        self._inherit_parent = value if self.can_inherit else False  # pylint: disable=using-constant-test

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
        """Parent page getter"""
        parent = self.__parent__
        page = get_portal_page(parent, page_name=self.name)
        while page.inherit_parent:
            parent = parent.__parent__
            page = get_portal_page(parent, page_name=self.name)
        return parent

    @property
    def use_local_template(self):
        """Local template usage getter"""
        return False if self.inherit_parent else self._use_local_template

    @use_local_template.setter
    def use_local_template(self, value):
        """Local template usage setter"""
        self._use_local_template = value
        if value and (self._local_template is None) and not self.inherit_parent:
            registry = get_pyramid_registry()
            template = get_object_factory(IPortalTemplate)()
            template.name = LOCAL_TEMPLATE_NAME
            self._local_template = template
            registry.notify(ObjectCreatedEvent(template))
            locate(template, self, '++template++')
        if self.use_local_template:
            alsoProvides(self, ILocalTemplateHandler)
        else:
            noLongerProvides(self, ILocalTemplateHandler)

    @property
    def local_template(self):
        """Local template getter"""
        return self._local_template

    @property
    def use_shared_template(self):
        """Shared template usage getter"""
        page = get_portal_page(self.parent, page_name=self.name)
        return page.use_shared_template if self.inherit_parent else not self._use_local_template

    @use_shared_template.setter
    def use_shared_template(self, value):
        """Shared template usage setter"""
        self.use_local_template = not value

    @property
    def shared_template(self):
        """Shared template getter"""
        return self.parent.shared_template \
            if self.inherit_parent else self._shared_template

    @shared_template.setter
    def shared_template(self, value):
        """Shared template setter"""
        if not self.inherit_parent:
            if IPortalTemplate.providedBy(value):  # pylint: disable=no-value-for-parameter
                value = IUniqueID(value).oid
            self._shared_template = value

    @property
    def template(self):
        """Template getter"""
        if self.inherit_parent:
            template = get_portal_page(self.parent, page_name=self.name).template
        else:
            if self.use_local_template:
                template = self.local_template
            else:
                template = self.shared_template
        if isinstance(template, str):
            template = query_utility(IPortalTemplate, name=template)
        return template


@adapter_config(required=IPortalContext,
                provides=IPortalPage)
def portal_context_page(context, page_name=''):
    """Portal context page factory"""

    def set_page_name(page):
        """Set page name after creation"""
        page.name = page_name

    key = f'{PORTAL_PAGE_KEY}::{page_name}' if page_name else PORTAL_PAGE_KEY
    return get_annotation_adapter(context, key, IPortalPage,
                                  name=f'++page++{page_name}',
                                  callback=set_page_name)


@adapter_config(name='header',
                required=IPortalHeaderContext,
                provides=IPortalPage)
def portal_context_header_page(context):
    """Portal context page header factory"""
    return portal_context_page(context, page_name='header')


@adapter_config(name='footer',
                required=IPortalFooterContext,
                provides=IPortalPage)
def portal_context_footer_page(context):
    """Portal context page footer factory"""
    return portal_context_page(context, page_name='footer')


@adapter_config(name='page',
                required=IPortalContext,
                provides=ITraversable)
class PortalContextPageTraverser(ContextAdapter):
    """Portal context page traverser"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Portal context page traverser"""
        return get_portal_page(self.context, page_name=name or '')


@adapter_config(name='template',
                required=IPortalPage,
                provides=ITraversable)
class PortalPageTemplateTraverser(ContextAdapter):
    """++template++ portal page traverser"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Portal page traverser to local template"""
        return self.context.local_template


@adapter_config(required=IPortalPage,
                provides=IPortalTemplateConfiguration)
def portal_page_template_configuration(context):
    """Portal context template configuration adapter"""
    return IPortalTemplateConfiguration(context.template)


@adapter_config(required=IPortalPage,
                provides=IPortalPortletsConfiguration)
def portal_page_portlets_configuration(context):
    """Portal page portlets configuration adapter"""

    def portlet_configuration_factory():
        return PortalPortletsConfiguration.clone(portlets_config, context)

    # get page and template
    if context.use_local_template:
        template = context.local_template
    else:
        template = context.template
    if template is None:
        return None
    portlets_config = IPortalPortletsConfiguration(template)
    if context.use_local_template:
        context = template
    # get current configuration
    config = get_annotation_adapter(context, PORTLETS_CONFIGURATION_KEY,
                                    factory=portlet_configuration_factory,
                                    notify=False, locate=False)
    # check for missing portlets configuration
    for portlet_id, portlet_config in portlets_config.items():
        if portlet_id not in config:
            config.set_portlet_configuration(portlet_id, clone(portlet_config))
    return config


@adapter_config(required=IPortalContext,
                provides=IPortalPortletsConfiguration)
def portal_context_portlets_configuration(context, page_name=''):
    """Portal context portlets configuration adapter"""
    page = get_portal_page(context, page_name=page_name)
    return IPortalPortletsConfiguration(page)


@adapter_config(name='header',
                required=IPortalContext,
                provides=IPortalPortletsConfiguration)
def portal_context_header_portlets_configuration(context):
    """Portal context header portlets configuration adapter"""
    return portal_context_portlets_configuration(context, 'header')


@adapter_config(name='footer',
                required=IPortalContext,
                provides=IPortalPortletsConfiguration)
def portal_context_footer_portlets_configuration(context):
    """Portal context footer portlets configuration adapter"""
    return portal_context_portlets_configuration(context, 'footer')


@adapter_config(name='portlet',
                required=IPortalPage,
                provides=ITraversable)
class PortalPagePortletTraverser(ContextAdapter):
    """++portlet++ portal page traverser"""

    def traverse(self, name, thurtherpath=None):  # pylint: disable=unused-argument
        """Portal context traverser to portlet configuration"""
        config = portal_context_portlets_configuration(self.context, page_name=self.context.name)
        if name:
            return config.get_portlet_configuration(int(name))
        return config
