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

"""PyAMS portal.interfaces module

Main portal management interfaces module.
"""

from zope.annotation import IAttributeAnnotatable
from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Attribute, Interface
from zope.location import ILocation
from zope.location.interfaces import IContained
from zope.schema import Bool, Choice, Int, List, Object, TextLine

from pyams_security.schema import PermissionField, PrincipalsSetField
from pyams_utils.schema import PersistentListField, PersistentMappingField

from pyams_portal import _  # pylint: disable=ungrouped-imports


MANAGE_TEMPLATE_PERMISSION = 'pyams_portal.ManageTemplate'
'''Permission used to manage templates'''

DESIGNER_ROLE = 'pyams.TemplatesManager'
'''Designer role is allowed to manage presentation templates'''


#
# Portlet interfaces
#

PORTLETS_VOCABULARY_NAME = 'pyams_portal.portlets'
'''Name of portlets vocabulary'''

PORTLET_RENDERERS_VOCABULARY = 'pyams_portal.portlet.renderers'
'''Name of portlet renderers vocabulary'''

TEMPLATE_SLOTS_VOCABULARY = 'pyams_portal.template.slots'
'''Name of template slots vocabulary'''


class IPortlet(Interface):
    """Portlet utility interface

    Portlets are registered utilities providing IPortlet
    """

    name = Attribute("Portlet internal name")

    label = Attribute("Portlet visible name")

    permission = PermissionField(title="Portlet permission",
                                 description="Permission required to display portlet",
                                 required=False)

    toolbar_image = Attribute("Portlet toolbar image")

    toolbar_css_class = Attribute("Portlet toolbar CSS class")

    settings_factory = Attribute("Portlet settings factory interface")


class IPortletCSSClass(Interface):
    """Portlet CSS class interface"""


class IPortletAddingInfo(Interface):
    """Portlet adding info interface"""

    portlet_name = Choice(title=_("Portlet"),
                          vocabulary=PORTLETS_VOCABULARY_NAME)

    slot_name = Choice(title=_("Slot name"),
                       description=_("Slot name to which this configuration applies"),
                       required=True,
                       vocabulary=TEMPLATE_SLOTS_VOCABULARY)


class IPortletSettings(ILocation, IAttributeAnnotatable):
    """Portlet settings interface

    Portlet settings is parented to it's configuration
    """

    configuration = Attribute("Settings parent configuration")

    renderer = Choice(title=_("Portlet renderer"),
                      description=_("Name of renderer used to render this portlet"),
                      vocabulary=PORTLET_RENDERERS_VOCABULARY,
                      required=False,
                      default='')

    def get_renderer(self, request=None):
        """Get renderer utility"""


PORTLETS_CONFIGURATION_KEY = 'pyams_portal.portlets'


class IPortletConfiguration(ILocation):
    """Portlet common configuration interface

    This is generic configuration settings common to all portlets.
    Portlet configuration is parented to:
     - it's template if parent is the template
     - it's context if parent is a portal context
    """

    portlet_id = Int(title="Portlet ID",
                     required=True)

    portlet_name = Attribute("Portlet name")

    def get_portlet(self):
        """Return portlet utility matching current portlet name"""

    can_inherit = Attribute("Can inherit parent configuration?")

    parent = Attribute("Portlet configuration parent")

    inherit_parent = Bool(title=_("Inherit parent configuration?"),
                          description=_("This option is only available if context's parent is "
                                        "using the same template..."),
                          required=True,
                          default=True)

    override_parent = Bool(title=_("Override parent configuration?"),
                           description=_("This option is only available if context's parent is "
                                         "using the same template..."),
                           required=True,
                           default=False)

    settings = Object(title="Portlet local settings",
                      schema=IPortletSettings,
                      readonly=True)

    editor_settings = Attribute("Editor settings")

    def get_settings(self, allow_inherit=True):
        """Get configuration settings, with or without inheritance"""


class IPortletContentProvider(IContentProvider):
    """Portlet content provider"""

    portlet = Object(title="Portlet utility",
                     schema=IPortlet)

    configuration = Object(title="Portlet renderer configuration",
                           schema=IPortletConfiguration)


class IPortletPreviewer(IPortletContentProvider):
    """Portlet previewer interface

    A portlet previewer should be defined as an adapter for a context,
    a request, a view and a portlet
    """


class IPortletRenderer(IPortletContentProvider):
    """Portlet renderer interface

    A portlet renderer should be defined as an adapter for a context,
    a request, a view and a portlet
    """

    label = Attribute("Renderer name")
    weight = Attribute("Renderer weight used for sorting")

    settings_interface = Attribute("Settings interface defined for this renderer")
    settings_key = Attribute("Annotations key used to store renderer settings")

    target_interface = Attribute("Target interface provided by this renderer")

    slot_configuration = Attribute("Template page slot configuration")
    renderer_settings = Attribute("Renderer settings")

    use_portlets_cache = Attribute("Can renderer use rendering cache?")
    use_authentication = Attribute("If 'True', portlet cache entry key is based on current "
                                   "authentication")

    def get_cache_key(self):
        """Defines key used to get/set portlet contents in cache"""

    resources = Attribute("Tuple of Fanstatic resources needed by this renderer")


PORTLET_RENDERER_SETTINGS_KEY = 'pyams_portal.renderer.settings::{0}'


class IPortletRendererSettings(Interface):
    """Portlet renderer settings interface"""


class IPortalPortletsConfiguration(IContained):
    """Portal template portlet configuration interface"""

    def get_portlet_configuration(self, portlet_id):
        """Get portlet configuration for given slot"""

    def set_portlet_configuration(self, portlet_id, config):
        """Set portlet configuration"""

    def delete_portlet_configuration(self, portlet_id):
        """Delete portlet configuration"""


#
# Slot interfaces
#

PORTAL_SLOTS_KEY = 'pyams_portal.slots'


class ISlot(Interface):
    """Portal template slot interface"""

    name = TextLine(title=_("Slot name"),
                    description=_("This name must be unique in a given template"),
                    required=True)

    row_id = Int(title=_("Row ID"),
                 required=False)


class ISlotConfiguration(Interface):
    """Portal slot configuration"""

    template = Attribute("Slot template")

    slot_name = TextLine(title="Slot name")

    portlet_ids = PersistentListField(title="Portlet IDs",
                                      value_type=Int())

    visible = Bool(title=_("Visible slot?"),
                   description=_("Select 'no' to hide this slot..."),
                   required=True,
                   default=True)

    container_css_class = TextLine(title=_("Container CSS class"),
                                   description=_("CSS class applied to this slot container"),
                                   required=False)

    xs_width = Int(title=_("Extra small device width"),
                   description=_("Slot width, in columns count, on extra small devices "
                                 "(&lt; 576 pixels); set to 0 to hide the slot"),
                   required=False,
                   min=0,
                   max=12)

    sm_width = Int(title=_("Small device width"),
                   description=_("Slot width, in columns count, on small devices "
                                 "(&gt;= 576 pixels); set to 0 to hide the slot"),
                   required=False,
                   min=0,
                   max=12)

    md_width = Int(title=_("Medium devices width"),
                   description=_("Slot width, in columns count, on medium desktop devices "
                                 "(&gt;= 768 pixels); set to 0 to hide the slot"),
                   required=False,
                   min=0,
                   max=12)

    lg_width = Int(title=_("Large devices width"),
                   description=_("Slot width, in columns count, on large desktop devices "
                                 "(&gt;= 992 pixels); set to 0 to hide the slot"),
                   required=False,
                   min=0,
                   max=12)

    xl_width = Int(title=_("Extra-large devices width"),
                   description=_("Slot width, in columns count, on extra large desktop devices "
                                 "(&gt;= 1200 pixels); set to 0 to hide the slot"),
                   required=False,
                   min=0,
                   max=12)

    css_class = TextLine(title=_("CSS class"),
                         description=_("CSS class applied to this slot"),
                         required=False)

    def get_css_class(self, device=None):
        """Get current CSS class"""

    def get_width(self, device=None):
        """Get slot width for each or given device"""

    def set_width(self, width, device=None):
        """Set width in columns count for given device"""


class ISlotRenderer(IContentProvider):
    """Slot renderer"""


#
# Template configuration interfaces
#

class IPortalTemplateConfiguration(IContained):
    """Portal template configuration interface"""

    # Rows configuration
    rows = Int(title="Rows count",
               required=True,
               default=1,
               min=0)

    def add_row(self):
        """Add new row"""

    def set_row_order(self, order):
        """Change template rows order"""

    def delete_row(self, row_id):
        """Delete template row"""

    # Slots configuration
    slot_names = PersistentListField(title="Slot names",
                                     value_type=TextLine())

    slot_order = PersistentMappingField(title="Slots order",
                                        key_type=Int(),  # row index
                                        value_type=PersistentListField(  # slot name
                                            value_type=TextLine()))

    slot_config = PersistentMappingField(title="Slots configuration",
                                         key_type=TextLine(),  # slot name
                                         value_type=Object(schema=ISlotConfiguration),
                                         required=False)

    def add_slot(self, slot_name, row_id=None):
        """Add slot with given name"""

    def set_slot_order(self, order):
        """Change template slots order"""

    def get_slot_row(self, slot_name):
        """Get row containing given slot"""

    def get_slots(self, row_id):
        """Get ordered list of slots for given row ID"""

    def get_slots_width(self, device=None):
        """Get slots width for given or all device(s)"""

    def set_slot_width(self, slot_name, device, width):
        """Set slot width for given device"""

    def get_slot_configuration(self, slot_name):
        """Get slot configuration for given slot"""

    def delete_slot(self, slot_name):
        """Delete template slot"""

    # Portlets configuration
    def add_portlet(self, portlet_name, slot_name):
        """Add portlet to given slot"""

    def get_portlet_slot(self, portlet_id):
        """Get row ID and slot for given portlet"""

    def set_portlet_order(self, order):
        """Set template portlets order"""

    def delete_portlet(self, portlet_id):
        """Delete template portlet"""


#
# Portal templates interfaces
#

LOCAL_TEMPLATE_NAME = '__local__'

TEMPLATE_CONFIGURATION_KEY = 'pyams_portal.template'

TEMPLATE_CONTAINER_CONFIGURATION_KEY = 'pyams_portal.container.configuration'

PORTAL_PAGE_KEY = 'pyams_portal.page'


class ILocalTemplateHandler(IAttributeAnnotatable):
    """Base interface for local template handler"""


PORTAL_TEMPLATES_VOCABULARY = 'pyams_portal.templates'
'''Name of portal templates vocabulary'''


class IPortalTemplate(ILocalTemplateHandler):
    """Portal template interface

    A portal template is a named utility providing a name and a set of slots containing portlets
    """

    name = TextLine(title=_("Template name"),
                    description=_("Explicit name given to portal template"),
                    required=True)

    css_class = TextLine(title=_("CSS class"),
                         description=_("This CSS class will be used as main template container "
                                       "CSS class"),
                         required=False)


class IPortalTemplateContainer(IContainer, IAttributeAnnotatable):
    """Portal template container interface"""

    contains(IPortalTemplate)

    last_portlet_id = Int(title="Last portlet ID",
                          required=True,
                          default=1,
                          min=0)

    def get_portlet_id(self):
        """Get new portlet ID"""


class IPortalTemplateContainerRoles(Interface):
    """Portal templates container roles interface"""

    designers = PrincipalsSetField(title=_("Designers"),
                                   description=_("List of designers allowed to manage "
                                                 "presentation templates"),
                                   role_id=DESIGNER_ROLE,
                                   required=False)


class IPortalTemplateContainerConfiguration(Interface):
    """Portal templates container configuration"""

    toolbar_portlets = List(title=_("Toolbar portlets"),
                            description=_("These portlets will be directly available in "
                                          "templates configuration page toolbar"),
                            value_type=Choice(vocabulary=PORTLETS_VOCABULARY_NAME),
                            required=False)


class IPortalTemplateRenderer(IContentProvider):
    """Portal template renderer

    A portal template renderer should be implemented as an adapter for a context, a request
    and a template
    """


PREVIEW_MODE = 'PREVIEW_MODE'


class IPortalPage(Interface):
    """Portal page interface

    The page is the highest configuration level.
    It defines which template is used (a shared or local one), which gives
    the slot and portlet lists.
    """

    can_inherit = Attribute("Can inherit parent template?")

    parent = Attribute("Parent from which to inherit, the real parent or the source template")

    inherit_parent = Bool(title=_("Inherit parent template?"),
                          description=_("Should we reuse parent template?"),
                          required=True,
                          default=True)

    override_parent = Bool(title=_("Override parent template?"),
                           description=_("Should we override parent template?"),
                           required=True,
                           default=False)

    use_local_template = Bool(title=_("Use local template?"),
                              description=_("If 'yes', you can define a custom local template "
                                            "instead of a shared template"),
                              required=True,
                              default=False)

    local_template = Object(title=_("Local template"),
                            schema=IPortalTemplate,
                            required=False,
                            readonly=True)

    use_shared_template = Bool(title=_("Use shared template?"),
                               description=_("If 'yes', you can select a shared template"),
                               required=True,
                               default=True)

    shared_template = Choice(title=_("Page template"),
                             description=_("Template used for this page"),
                             vocabulary=PORTAL_TEMPLATES_VOCABULARY,
                             required=False)

    template = Attribute("Used template")


class IPortalContext(IAttributeAnnotatable):
    """Portal context marker interface"""
