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

"""PyAMS_portal.template module

This module defines base template configuration components.
"""

from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from pyramid.events import subscriber
from zope.container.contained import Contained
from zope.container.folder import Folder
from zope.interface import implementer
from zope.lifecycleevent import IObjectAddedEvent, IObjectRemovedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.interfaces import ITraversable

from pyams_portal.interfaces import IPortalPortletsConfiguration, IPortalTemplate, \
    IPortalTemplateConfiguration, IPortalTemplateContainer, IPortalTemplateContainerConfiguration, \
    IPortalTemplateContainerRoles, IPortlet, IPortletConfiguration, \
    MANAGE_TEMPLATE_PERMISSION, PORTAL_TEMPLATES_VOCABULARY, PORTLETS_CONFIGURATION_KEY, \
    TEMPLATE_CONFIGURATION_KEY, TEMPLATE_CONTAINER_CONFIGURATION_KEY, TEMPLATE_SLOTS_VOCABULARY
from pyams_portal.slot import SlotConfiguration
from pyams_security.interfaces import IDefaultProtectionPolicy, IRolesPolicy, \
    IViewContextPermissionChecker
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_site.interfaces import ISiteRoot
from pyams_utils.adapter import ContextAdapter, adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import get_pyramid_registry, get_utility
from pyams_utils.request import check_request
from pyams_utils.traversing import get_parent
from pyams_utils.vocabulary import LocalUtilitiesVocabulary, vocabulary_config


__docformat__ = 'restructuredtext'


#
# Portal templates container
#

@factory_config(IPortalTemplateContainer)
@implementer(IDefaultProtectionPolicy)
class PortalTemplateContainer(ProtectedObjectMixin, Folder):
    """Portal templates container"""

    show_home_menu = FieldProperty(IPortalTemplateContainer['show_home_menu'])
    last_portlet_id = FieldProperty(IPortalTemplateContainer['last_portlet_id'])

    def get_portlet_id(self):
        """New portlet ID getter"""
        self.last_portlet_id += 1
        return self.last_portlet_id


@implementer(IPortalTemplateContainerRoles)
class PortalTemplateContainerRoles(ProtectedObjectRoles):
    """Portal template container roles"""

    designers = RolePrincipalsFieldProperty(IPortalTemplateContainerRoles['designers'])


@adapter_config(required=IPortalTemplateContainer,
                provides=IPortalTemplateContainerRoles)
def portal_template_container_roles_adapter(context):
    """Portal template container roles adapter"""
    return PortalTemplateContainerRoles(context)


@adapter_config(name='template_container_roles',
                required=IPortalTemplateContainer,
                provides=IRolesPolicy)
class PortalTemplateContainerRolesPolicy(ContextAdapter):
    """Portal template container roles policy"""

    roles_interface = IPortalTemplateContainerRoles
    weight = 20


@factory_config(IPortalTemplateContainerConfiguration)
class PortalTemplateContainerConfiguration(Persistent, Contained):
    """Portal template container configuration"""

    toolbar_portlets = FieldProperty(IPortalTemplateContainerConfiguration['toolbar_portlets'])


@adapter_config(required=IPortalTemplateContainer,
                provides=IPortalTemplateContainerConfiguration)
def portal_template_container_configuration_adapter(context):
    """Portal template container configuration factory"""
    return get_annotation_adapter(context, TEMPLATE_CONTAINER_CONFIGURATION_KEY,
                                  IPortalTemplateContainerConfiguration)


#
# Portal template base class
#

@factory_config(IPortalTemplate)
class PortalTemplate(Persistent, Contained):
    """Portal template class"""

    name = FieldProperty(IPortalTemplate['name'])
    css_class = FieldProperty(IPortalTemplate['css_class'])


@subscriber(IObjectAddedEvent, context_selector=IPortalTemplate)
def handle_added_template(event):
    """Register shared template"""
    sm = get_parent(event.newParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        template = event.object
        sm.getSiteManager().registerUtility(template, IPortalTemplate,
                                            name=IUniqueID(template).oid)


@subscriber(IObjectRemovedEvent, context_selector=IPortalTemplate)
def handle_removed_template(event):
    """Unregister removed template"""
    sm = get_parent(event.oldParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        template = event.object
        sm.getSiteManager().unregisterUtility(template, IPortalTemplate,
                                              name=IUniqueID(template).oid)


@adapter_config(required=IPortalTemplate, provides=IViewContextPermissionChecker)
class PortalTemplatePermissionChecker(ContextAdapter):
    """Portal template permission checker"""

    edit_permission = MANAGE_TEMPLATE_PERMISSION


@vocabulary_config(name=PORTAL_TEMPLATES_VOCABULARY)
class PortalTemplatesVocabulary(LocalUtilitiesVocabulary):
    """Portal templates vocabulary"""

    interface = IPortalTemplate


#
# Portal template configuration
#

@factory_config(IPortalTemplateConfiguration)
class PortalTemplateConfiguration(Persistent, Contained):
    """Portal template configuration"""

    rows = FieldProperty(IPortalTemplateConfiguration['rows'])
    _slot_names = FieldProperty(IPortalTemplateConfiguration['slot_names'])
    _slot_order = FieldProperty(IPortalTemplateConfiguration['slot_order'])
    _slot_config = FieldProperty(IPortalTemplateConfiguration['slot_config'])

    def __init__(self):
        self._slot_names = PersistentList()
        self._slot_order = PersistentMapping()
        self._slot_order[0] = PersistentList()
        self.slot_config = PersistentMapping()

    # rows management

    def add_row(self):
        """Add new row and return last row index (0 based)"""
        self.rows += 1
        last_index = self.rows - 1
        self.slot_order[last_index] = PersistentList()
        return last_index

    def set_row_order(self, order):
        """Change template row order"""
        if not isinstance(order, (list, tuple)):
            order = list(order)
        old_slot_order = self.slot_order
        assert len(order) == self.rows
        new_slot_order = PersistentMapping()
        for index, row_id in enumerate(order):
            new_slot_order[index] = old_slot_order.get(row_id) or PersistentList()
        if self.slot_order != new_slot_order:
            self.slot_order = new_slot_order

    def delete_row(self, row_id):
        """Delete template row"""
        assert row_id in self.slot_order
        for slot_name in self.slot_order.get(row_id, ()):
            config = IPortalPortletsConfiguration(self.__parent__)
            config.delete_portlet_configuration(self.slot_config[slot_name].portlet_ids)
            if slot_name in self.slot_names:
                self.slot_names.remove(slot_name)
            if slot_name in self.slot_config:
                del self.slot_config[slot_name]
        for index in range(row_id, self.rows - 1):
            self.slot_order[index] = self.slot_order[index + 1]
        if self.rows > 0:
            del self.slot_order[self.rows - 1]
        self.rows -= 1

    # slots management

    @property
    def slot_names(self):
        """Slot names getter"""
        return self._slot_names

    @slot_names.setter
    def slot_names(self, value):
        """Slot names setter"""
        self._slot_names = value

    @property
    def slot_order(self):
        """Slot order getter"""
        return self._slot_order

    @slot_order.setter
    def slot_order(self, value):
        """Slot order setter"""
        self._slot_order = value

    @property
    def slot_config(self):
        """Slot configuration getter"""
        return self._slot_config

    @slot_config.setter
    def slot_config(self, value):
        """Slot configuration setter"""
        self._slot_config = value

    def add_slot(self, slot_name, row_id=None):
        """Add new slot to template"""
        assert slot_name not in self.slot_names
        self.slot_names.append(slot_name)
        if row_id is None:
            row_id = 0
        assert 0 <= row_id < self.rows
        # init slots order
        if row_id not in self.slot_order:
            self.slot_order[row_id] = PersistentList()
        self.slot_order[row_id].append(slot_name)
        # init slots configuration
        slot = self.slot_config[slot_name] = SlotConfiguration(slot_name)
        locate(slot, self.__parent__)
        return row_id, slot_name

    def set_slot_order(self, order):
        """Set template slots order"""
        old_slot_order = self.slot_order
        new_slot_order = PersistentMapping()
        for row_id in sorted(map(int, order.keys())):
            new_slot_order[row_id] = PersistentList(order[row_id])
        if new_slot_order != old_slot_order:
            self.slot_order = new_slot_order

    def get_slot_row(self, slot_name):
        """Get row associated with given slot"""
        for row_id in self.slot_order:
            if slot_name in self.slot_order[row_id]:
                return row_id
        return None

    def get_slots(self, row_id):
        """Get ordered slots list"""
        return self.slot_order.get(row_id, [])

    def get_slots_width(self, device=None):
        """Get slots width for given device"""
        result = {}
        for slot_name, config in self.slot_config.items():
            result[slot_name] = config.get_width(device)
            result[slot_name]['css'] = config.get_css_class(device)
            result[slot_name]['visible'] = config.visible
        return result

    def set_slot_width(self, slot_name, device, width):
        """Set slot width for given device"""
        self.slot_config[slot_name].set_width(width, device)

    def get_slot_configuration(self, slot_name):
        """Get slot configuration"""
        if slot_name not in self.slot_names:
            return None
        config = self.slot_config.get(slot_name)
        if config is None:
            self.slot_config[slot_name] = config = SlotConfiguration()
            locate(config, self.__parent__)
        return config

    def delete_slot(self, slot_name):
        """Delete slot and associated portlets"""
        assert slot_name in self.slot_names
        row_id = self.get_slot_row(slot_name)
        # delete portlet configuration
        config = IPortalPortletsConfiguration(self.__parent__)
        config.delete_portlet_configuration(self.slot_config[slot_name].portlet_ids)
        # delete slot configuration
        del self.slot_config[slot_name]
        self.slot_order[row_id].remove(slot_name)
        self.slot_names.remove(slot_name)

    # portlets management

    def add_portlet(self, portlet_name, slot_name):
        """Add portlet to given slot"""
        assert slot_name in self.slot_names
        # get new portlet configuration
        portlet = get_pyramid_registry().getUtility(IPortlet, name=portlet_name)
        config = IPortletConfiguration(portlet)
        # store portlet configuration
        manager = get_utility(IPortalTemplateContainer)
        IPortalPortletsConfiguration(self.__parent__).set_portlet_configuration(
            manager.get_portlet_id(), config)
        # update slots configuration
        self.slot_config[slot_name].portlet_ids.append(config.portlet_id)
        return {
            'portlet_name': portlet_name,
            'portlet_id': config.portlet_id,
            'slot_name': slot_name,
            'position': len(self.slot_config[slot_name].portlet_ids) - 1,
            'label': check_request().localizer.translate(portlet.label)
        }

    def get_portlet_slot(self, portlet_id):
        """Get portlet slot"""
        for slot_name, config in self.slot_config.items():
            if portlet_id in config.portlet_ids:
                return self.get_slot_row(slot_name), slot_name
        return None, None

    def set_portlet_order(self, order):
        """Set portlet order"""
        _from_row, from_slot = self.get_portlet_slot(order['from'])
        if from_slot is None:
            return
        target_slot = order['to']['slot']
        target_row = self.get_slot_row(target_slot)
        if target_row is None:
            return
        self.slot_config[from_slot].portlet_ids.remove(order['from'])
        self.slot_config[target_slot].portlet_ids = PersistentList(order['to']['portlet_ids'])

    def delete_portlet(self, portlet_id):
        """Delete portlet"""
        _row_id, slot_name = self.get_portlet_slot(portlet_id)
        if slot_name is not None:
            self.slot_config[slot_name].portlet_ids.remove(portlet_id)
            IPortalPortletsConfiguration(self.__parent__).delete_portlet_configuration(portlet_id)


@adapter_config(required=IPortalTemplate,
                provides=IPortalTemplateConfiguration)
def portal_template_configuration_factory(context):
    """Portal template configuration adapter"""
    return get_annotation_adapter(context, TEMPLATE_CONFIGURATION_KEY,
                                  IPortalTemplateConfiguration)


@vocabulary_config(name=TEMPLATE_SLOTS_VOCABULARY)
class PortalTemplateSlotsVocabulary(SimpleVocabulary):
    """Portal template slots vocabulary"""

    def __init__(self, context):
        config = IPortalTemplateConfiguration(context)
        terms = [
            SimpleTerm(slot_name, title=slot_name)
            for slot_name in sorted(config.slot_names)
        ]
        super().__init__(terms)


@adapter_config(name='portlet',
                required=IPortalTemplate,
                provides=ITraversable)
class PortalTemplatePortletTraverser(ContextAdapter):
    """++portlet++ template traverser"""

    def traverse(self, name, furtherpath=None):  # pylint: disable=unused-argument
        """Portal template traverser to portlet configuration"""
        config = IPortalPortletsConfiguration(self.context)
        if name:
            return config.get_portlet_configuration(int(name))
        return config


#
# Template portlets configuration
#

@adapter_config(required=IPortalTemplate,
                provides=IPortalPortletsConfiguration)
def portal_template_portlets_configuration_adapter(template):
    """Portal template portlets configuration adapter"""
    return get_annotation_adapter(template, PORTLETS_CONFIGURATION_KEY,
                                  IPortalPortletsConfiguration)
