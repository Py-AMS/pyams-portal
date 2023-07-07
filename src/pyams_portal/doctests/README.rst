====================
PyAMS portal package
====================

Introduction
------------

This package is composed of a set of components, usable into any PyAMS application, which can be used to provide
presentation templates.

A template is using a Bootstrap based structure, made of rows and "slots" which are containers which can be sized
and placed according to device size. A slot can then contain "portlets", which are small components which can contain
text, images or whatever required content.

Templates can be local to a given context, or stored in a central repository and shared between several contents.
Moreover, any content which is placed inside a hierarchy can choose to inherit template from it's parent, or define
it's own configuration; but even if you inherit from parent of use a shared template, each portlet settings can be
reused as is, or redefined, individually.

To improve rendering performances, each portlet render result can be cached.

    >>> import pprint
    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> from pyams_utils.request import get_annotations

    >>> config = setUp(hook_zca=True)
    >>> config.add_request_method(get_annotations, 'annotations', reify=True)
    >>> config.registry.settings['zodbconn.uri'] = 'memory://'

    >>> from pyramid_zodbconn import includeme as include_zodbconn
    >>> include_zodbconn(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)
    >>> from pyams_viewlet import includeme as include_viewlet
    >>> include_viewlet(config)
    >>> from pyams_pagelet import includeme as include_pagelet
    >>> include_pagelet(config)
    >>> from pyams_i18n import includeme as include_i18n
    >>> include_i18n(config)
    >>> from pyams_security import includeme as include_security
    >>> include_security(config)
    >>> from pyams_catalog import includeme as include_catalog
    >>> include_catalog(config)
    >>> from pyams_form import includeme as include_form
    >>> include_form(config)
    >>> from pyams_portal import includeme as include_portal
    >>> include_portal(config)

    >>> from zope.interface import alsoProvides
    >>> from pyams_site.generations import upgrade_site
    >>> from pyams_layer.interfaces import IPyAMSLayer

    >>> request = DummyRequest(scheme='http')
    >>> alsoProvides(request, IPyAMSLayer)

    >>> app = upgrade_site(request)
    Upgrading PyAMS I18n to generation 1...
    Upgrading PyAMS catalog to generation 1...
    Upgrading PyAMS security to generation 2...
    Upgrading PyAMS portal to generation 5...

    >>> from pyramid_chameleon.zpt import renderer_factory
    >>> config.add_renderer('.pt', renderer_factory)

    >>> from pyramid.threadlocal import manager
    >>> from pyams_portal.interfaces import IPortalContext

    >>> alsoProvides(app, IPortalContext)
    >>> request.root = app
    >>> manager.push({'request': request, 'registry': request.registry})

    >>> from pyams_utils.registry import handle_site_before_traverse
    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> handle_site_before_traverse(BeforeTraverseEvent(app, request))

    >>> from pyams_utils.registry import get_utility
    >>> from pyams_portal.interfaces import IPortalTemplateContainer
    >>> ptc = get_utility(IPortalTemplateContainer)
    >>> ptc
    <pyams_portal.template.PortalTemplateContainer object at 0x...>


Portal templates
----------------

A template is a presentation component made of rows containing slots containing portlets.
Rows are always "full-width" components, while slots can be configured using a Bootstrap grid;
portlets are then full-width inside a slot.

Let's create a first template:

    >>> from pyams_utils.factory import get_object_factory
    >>> from pyams_portal.interfaces import IPortalTemplate

    >>> factory = get_object_factory(IPortalTemplate)
    >>> template = factory()
    >>> template
    <pyams_portal.template.PortalTemplate object at 0x...>
    >>> template.name = 'First template'

    >>> from zope.lifecycleevent import ObjectAddedEvent
    >>> ptc['first'] = template
    >>> request.registry.notify(ObjectAddedEvent(template, ptc))

    >>> from pyams_utils.interfaces.intids import IUniqueID
    >>> get_utility(IPortalTemplate, name=IUniqueID(template).oid) is template
    True

    >>> from pyams_portal.interfaces import IPortalTemplateConfiguration
    >>> template_config = IPortalTemplateConfiguration(template)
    >>> template_config
    <pyams_portal.template.PortalTemplateConfiguration object at 0x...>
    >>> template_config.rows
    1
    >>> template_config.slot_order[0]
    []

    >>> row_index = template_config.add_row()
    >>> row_index
    1
    >>> template_config.rows
    2

Let's create a new slot:

    >>> row_id, name = template_config.add_slot('Slot 1')
    >>> row_id, name
    (0, 'Slot 1')
    >>> template_config.get_slots(0)
    ['Slot 1']

    >>> template_config.slot_names
    ['Slot 1']
    >>> template_config.slot_order
    {0: ['Slot 1'], 1: []}
    >>> template_config.get_slot_row('Slot 1')
    0
    >>> template_config.get_slots(0)
    ['Slot 1']

    >>> template_config.slot_config
    {'Slot 1': <pyams_portal.slot.SlotConfiguration object at 0x...>}
    >>> template_config.get_slot_configuration('Slot 1')
    <pyams_portal.slot.SlotConfiguration object at 0x...>
    >>> template_config.get_slot_configuration('missing') is None
    True

    >>> template_config.get_slots_width()
    {'Slot 1': {'xs': 12, 'sm': 12, 'md': 12, 'lg': 12, 'xl': 12, 'css': 'col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12', 'visible': True}}
    >>> template_config.set_slot_width('Slot 1', 'md', 6)
    >>> template_config.get_slots_width('md')
    {'Slot 1': {'md': 6, 'css': 'col  col-md-6', 'visible': True}}

We can than add a new slot:

    >>> template_config.add_slot('Slot 2', row_id=1)
    (1, 'Slot 2')
    >>> template_config.add_slot('Slot 3', row_id=1)
    (1, 'Slot 3')

    >>> template_config.slot_order
    {0: ['Slot 1'], 1: ['Slot 2', 'Slot 3']}

A slot can be moved from one row to another:

    >>> template_config.set_slot_order({0: ['Slot 1', 'Slot 3'], 1: ['Slot 2']})
    >>> template_config.slot_order
    {0: ['Slot 1', 'Slot 3'], 1: ['Slot 2']}

We can also delete a slot:

    >>> template_config.delete_slot('Slot 3')
    >>> template_config.slot_order
    {0: ['Slot 1'], 1: ['Slot 2']}

We can also change rows order, or delete a row:

    >>> template_config.set_row_order([1, 0])
    >>> template_config.slot_order
    {0: ['Slot 2'], 1: ['Slot 1']}

    >>> template_config.delete_row(0)
    >>> template_config.slot_order
    {0: ['Slot 1']}


Configuring slots
-----------------

Each slot can configured using a number of properties:

    >>> template_config.get_slot_configuration('Slot 2') is None
    True
    >>> slot_configuration = template_config.get_slot_configuration('Slot 1')
    >>> slot_configuration
    <pyams_portal.slot.SlotConfiguration object at 0x...>

    >>> slot_configuration.visible
    True
    >>> slot_configuration.container_css_class is None
    True
    >>> slot_configuration.md_width
    6
    >>> slot_configuration.template is template
    True


Adding portlets
---------------

A portlet is a named utility providing IPortlet interface, which is registered using
the "portlet_config" decorator; some portlets are provided by PyAMS_portal package.

A portlets vocabulary is available:

    >>> from pyams_portal.portlet import PortletVocabulary
    >>> vocabulary = PortletVocabulary(app)
    >>> pprint.pprint(vocabulary.by_token)
    {'pyams_portal.portlet.cards': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.carousel': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.html': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.image': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.jumbotron': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.raw': <zope.schema.vocabulary.SimpleTerm object at 0x...>,
     'pyams_portal.portlet.spacer': <zope.schema.vocabulary.SimpleTerm object at 0x...>}

    >>> from pyams_portal.portlets.html import HTML_PORTLET_NAME

    >>> portlet = template_config.add_portlet(HTML_PORTLET_NAME, 'Slot 1')
    >>> pprint.pprint(portlet)
    {'label': 'Rich text',
     'portlet_id': 2,
     'portlet_name': 'pyams_portal.portlet.html',
     'position': 0,
     'slot_name': 'Slot 1'}

    >>> template_config.get_portlet_slot(2)
    (0, 'Slot 1')

The same portlet can be added several times in a same slot:

    >>> portlet2 = template_config.add_portlet(HTML_PORTLET_NAME, 'Slot 1')
    >>> pprint.pprint(portlet2)
    {'label': 'Rich text',
     'portlet_id': 3,
     'portlet_name': 'pyams_portal.portlet.html',
     'position': 1,
     'slot_name': 'Slot 1'}

We can then change portlets order:

    >>> template_config.set_portlet_order({'from': 3, 'to': {'slot': 'Slot 1', 'portlet_ids': [3, 2]}})
    >>> template_config.get_slot_configuration('Slot 1').portlet_ids
    [3, 2]

Providing bad IDs doesn't change anything:

    >>> template_config.set_portlet_order({'from': 4, 'to': {'slot': 'Slot 1', 'portlet_ids': [4, 1]}})
    >>> template_config.get_slot_configuration('Slot 1').portlet_ids
    [3, 2]


Updating portlet configuration
------------------------------

Portlet configuration is defined for each portlet:

    >>> from pyams_portal.interfaces import IPortalPortletsConfiguration

    >>> portlets_config = IPortalPortletsConfiguration(template)
    >>> pprint.pprint(portlets_config)
    {2: <pyams_portal.portlet.PortletConfiguration object at 0x...>,
     3: <pyams_portal.portlet.PortletConfiguration object at 0x...>}

    >>> portlet_config = portlets_config[2]
    >>> portlet_config.can_inherit
    False
    >>> portlet_config.inherit_parent
    False
    >>> portlet_config.override_parent
    True
    >>> portlet_config.parent is template
    True

    >>> settings = portlet_config.settings
    >>> settings
    <pyams_portal.portlets.html.HTMLPortletSettings object at 0x...>

    >>> portlet_config.get_settings(allow_inherit=True) is settings
    True
    >>> portlet_config.get_settings(allow_inherit=False) is settings
    True

    >>> settings.configuration is portlet_config
    True
    >>> settings.visible
    True
    >>> settings.renderer
    ''
    >>> settings.get_renderer(request)
    <pyams_portal.portlets.html.skin.HTMLPortletDefaultRenderer object at 0x...>

    >>> settings.body = {'en': '<p>This is my body!</p>'}


Setting portlet renderer
------------------------

    >>> settings.renderer = 'hidden'
    >>> settings.renderer
    'hidden'
    >>> settings.get_renderer(request)
    <pyams_portal.skin.HiddenPortletRenderer object at 0x...>
    >>> settings.visible
    False


Setting portlet renderer with custom settings
---------------------------------------------

Some renderers can need custom settings which are not defined for the whole portlet but
only for a specific renderer; the settings factory is defined by the renderer's
*settings_interface* attribute.

Let's try to add another portlet:

    >>> from pyams_portal.portlets.html import RAW_PORTLET_NAME
    >>> portlet3 = template_config.add_portlet(RAW_PORTLET_NAME, 'Slot 1')
    >>> portlet3['portlet_id']
    4
    >>> portlet_config = portlets_config[4]
    >>> portlet_config.get_portlet()
    <pyams_portal.portlets.html.RawPortlet object at 0x...>

    >>> settings = portlet_config.settings
    >>> settings.renderer = 'source-code'
    >>> renderer = settings.get_renderer(request)
    >>> renderer.settings is settings
    True
    >>> renderer.renderer_settings
    <pyams_utils.pygments.PygmentsCodeRendererSettings object at 0x...>


Portlets adapters
-----------------

    >>> from pyams_portal.interfaces import IPortletSettings
    >>> IPortletSettings(portlet_config) is settings
    True

    >>> from pyams_portal.interfaces import IPortletConfiguration
    >>> IPortletConfiguration(settings) is portlet_config
    True


Deleting portlet
----------------

    >>> template_config.delete_portlet(3)
    >>> template_config.get_slot_configuration('Slot 1').portlet_ids
    [2, 4]


Defining a portal page
----------------------

A portal *page* is a template definition which can be applied on a portal *context*; a portal
context is defined by implementing the *IPortalContext* interface:

    >>> from pyams_portal.interfaces import IPortalPage
    >>> page = IPortalPage(app)
    >>> page
    <pyams_portal.page.PortalPage object at 0x...>

A portal page can choose to use a shared template, to use a local template or to inherit from
it's parent template, if any:

    >>> page.parent is app
    True
    >>> page.can_inherit
    False
    >>> page.inherit_parent
    False
    >>> page.override_parent
    True

Choosing to inherit has no effect when you can't inherit:

    >>> page.override_parent = False
    >>> page.override_parent
    True

    >>> page.use_shared_template = True

    >>> page.shared_template = template
    >>> page.shared_template == IUniqueID(template).oid
    True
    >>> page.use_shared_template
    True
    >>> page.template is template
    True

The *check_local_template* function is available to check actions that can only be applied
on a local template:

    >>> from pyams_portal.page import check_local_template
    >>> check_local_template(app)
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPBadRequest: Action can be done only on local templates!


A portal page is then getting it's slots configuration from it's selected template, but each
portlet can override it's configuration:

    >>> from pyams_portal.interfaces import IPortalTemplateConfiguration
    >>> IPortalTemplateConfiguration(page) is template_config
    True

    >>> from pyams_portal.interfaces import IPortalPortletsConfiguration
    >>> IPortalPortletsConfiguration(page) is portlets_config
    False
    >>> page_portlets_config = IPortalPortletsConfiguration(app)
    >>> pprint.pprint(page_portlets_config)
    {2: <pyams_portal.portlet.PortletConfiguration object at 0x...>,
     4: <pyams_portal.portlet.PortletConfiguration object at 0x...>}

    >>> page_portlets_config[2].can_inherit
    True
    >>> page_portlets_config[2].inherit_parent
    True
    >>> page_portlets_config[2].settings.body
    {'en': '<p>This is my body!</p>'}

Please note however that a clone of original portlet configuration is created on first access:

    >>> page_portlets_config[2] is portlets_config[2]
    False
    >>> page_portlets_config[2].get_settings(allow_inherit=True) is page_portlets_config[2].settings
    True
    >>> page_portlets_config[2].get_settings(allow_inherit=False) is page_portlets_config[2].settings
    False


Changing portlet settings require to override from parent:

    >>> page_portlets_config[2].settings.body = {'en': '<p>This is my modified body!</p>'}
    >>> page_portlets_config[2].settings.body
    {'en': '<p>This is my modified body!</p>'}
    >>> portlets_config[2].settings.body
    {'en': '<p>This is my modified body!</p>'}

While still inheriting from parent, a modification is applied to portlet from which we inherit!
We have to break inheritance to apply local modifications:

    >>> page_portlets_config[2].override_parent = True
    >>> page_portlets_config[2].settings.body = {'en': '<p>This is my second modified body!</p>'}
    >>> page_portlets_config[2].settings.body
    {'en': '<p>This is my second modified body!</p>'}
    >>> portlets_config[2].settings.body
    {'en': '<p>This is my modified body!</p>'}


Using local template
--------------------

Instead of using a shared template, we can always choose to use a local template:

    >>> page.use_local_template = True
    >>> page.template is template
    False
    >>> page.template.__name__
    '++template++'

    >>> check_local_template(app)

    >>> app_template = IPortalTemplateConfiguration(page)
    >>> app_template
    <pyams_portal.template.PortalTemplateConfiguration object at 0x...>
    >>> app_template.rows
    1
    >>> app_template.slot_order[0]
    []
    >>> pprint.pprint(IPortalPortletsConfiguration(app))
    {}

The new template is empty; we can add slots and portlets as we did with the shared template:

    >>> row_id, name = app_template.add_slot('Slot 1')
    >>> row_id, name
    (0, 'Slot 1')
    >>> portlet = app_template.add_portlet(HTML_PORTLET_NAME, 'Slot 1')
    >>> pprint.pprint(portlet)
    {'label': 'Rich text',
     'portlet_id': 5,
     'portlet_name': 'pyams_portal.portlet.html',
     'position': 0,
     'slot_name': 'Slot 1'}
    >>> pprint.pprint(IPortalPortletsConfiguration(app))
    {5: <pyams_portal.portlet.PortletConfiguration object at 0x...>}

You can notice here that portlets IDs are not defined for a template, but globally.


Templates inheritance
---------------------

When defining sub-levels, you can choose to apply a shared template or a local template,
but you can also choose to inherit from parent level:

    >>> from zope.container.folder import Folder
    >>> folder = Folder()
    >>> alsoProvides(folder, IPortalContext)
    >>> app['folder'] = folder

    >>> folder_page = IPortalPage(folder)
    >>> folder_page.can_inherit
    True
    >>> folder_page.inherit_parent
    True

    >>> IPortalTemplateConfiguration(folder_page) is app_template
    True

    >>> folder_portlets = IPortalPortletsConfiguration(folder)
    >>> pprint.pprint(folder_portlets)
    {5: <pyams_portal.portlet.PortletConfiguration object at 0x...>}
    >>> folder_portlets.get_portlet_configuration(5)
    <pyams_portal.portlet.PortletConfiguration object at 0x...>

    >>> folder_portlets[5].parent is page
    True

If we create a new portlet in parent template after initialization, we always get a clone of it's
configuration in the inherited template:

    >>> portlet = app_template.add_portlet(HTML_PORTLET_NAME, 'Slot 1')
    >>> portlet['portlet_id']
    6
    >>> folder_portlets.get_portlet_configuration(6)
    <pyams_portal.portlet.PortletConfiguration object at 0x...>

    >>> folder_portlets = IPortalPortletsConfiguration(folder)
    >>> pprint.pprint(folder_portlets)
    {5: <pyams_portal.portlet.PortletConfiguration object at 0x...>,
     6: <pyams_portal.portlet.PortletConfiguration object at 0x...>}

    >>> folder_portlets[6].settings.body = {'en': '<p>This is a test!</p>'}


Previewing portlets
-------------------

Portlets preview is used to display main settings of a given portlet in the management
interface; it's not a "real" preview, as the final look essentially depends on the
graphical theme which will be applied.

    >>> from pyams_portal.interfaces import IPortletPreviewer

    >>> settings = folder_portlets[5].settings
    >>> previewer = request.registry.queryMultiAdapter((folder, request, None, settings), IPortletPreviewer)
    >>> previewer
    <pyams_portal.portlets.html.zmi.HTMLPortletPreviewer object at 0x...>

    >>> previewer.slot_configuration
    <pyams_portal.slot.SlotConfiguration object at 0x...>

    >>> print(previewer.get_setting(settings, 'body'))
    <div>
        <small><strong>Body :</strong></small> --
    </div>

    >>> print(previewer())
    <div class="text-info text-truncate border-bottom mb-1">
        <small>Renderer:</small>    Rich text (default)
        <span class="float-right"><i class="fa fa-fw fas fa-mobile-alt hint" title="Smartphones"></i> <i class="fa fa-fw fas fa-tablet-alt hint" title="Tablets"></i> <i class="fa fa-fw fas fa-desktop hint" title="Medium screens"></i> <i class="fa fa-fw fas fa-tv hint" title="Large screens"></i> <i class="fa fa-fw fas fa-solar-panel hint" title="Extra large screens"></i></span>
    </div>--

    >>> settings = folder_portlets[6].settings
    >>> previewer = request.registry.queryMultiAdapter((folder, request, None, settings), IPortletPreviewer)

    >>> print(previewer.get_setting(settings, 'body'))
    <div class="text-truncate">
        <small><strong>Body :</strong></small>
        <p>This is a test!</p>
    </div>

    >>> print(previewer())
    <div class="text-info text-truncate border-bottom mb-1">
        <small>Renderer:</small>    Rich text (default)
        <span class="float-right"><i class="fa fa-fw fas fa-mobile-alt hint" title="Smartphones"></i> <i class="fa fa-fw fas fa-tablet-alt hint" title="Tablets"></i> <i class="fa fa-fw fas fa-desktop hint" title="Medium screens"></i> <i class="fa fa-fw fas fa-tv hint" title="Large screens"></i> <i class="fa fa-fw fas fa-solar-panel hint" title="Extra large screens"></i></span>
    </div><p>This is a test!</p>


Rendering portlets
------------------

Portlets are rendered using renderers. A renderer is a registered adapter which is usually
relying on a template to do it's rendering.

    >>> folder_portlets[6].settings.get_devices_visibility()
    'd-block d-sm-block d-md-block d-lg-block d-xl-block'

    >>> renderer = folder_portlets[6].settings.get_renderer()
    >>> renderer
    <pyams_portal.portlets.html.skin.HTMLPortletDefaultRenderer object at 0x...>
    >>> renderer.slot_configuration
    <pyams_portal.slot.SlotConfiguration object at 0x...>

Portlets renderers can use a shared cache to store their content for a short duration; this
cache is never used in preview mode.

    >>> renderer.use_portlets_cache
    True

Rendering portlets requires a matching cache region:

    >>> from beaker.cache import CacheManager, cache_regions
    >>> cache = CacheManager(**{'cache.type': 'memory'})
    >>> cache_regions.update({'portlets': {'type': 'memory', 'expire': 60}})

The cache key is based on the current hostname, on the context and on the current locale:

    >>> renderer.get_cache_key()
    'portlet::http::example.com:80::...::1::en'
    >>> renderer.render()
    '<p>This is a test!</p>'

A second rendering should use the cache:

    >>> renderer.render()
    '<p>This is a test!</p>'

The 'hidden' renderer just returns an empty string:

    >>> folder_portlets[6].settings.override_parent = True
    >>> folder_portlets[6].settings.renderer = 'hidden'
    >>> folder_portlets[6].settings.get_renderer().render()
    ''

    >>> folder_portlets[6].settings.renderer = ''
    >>> folder_portlets[6].settings.override_parent = False


Custom renderer template
------------------------

You can provide a specific template name when rendering a portlet; if this specific template
is not registered for this renderer, the default template is used:

    >>> folder_portlets[6].settings.get_renderer().render(template_name='custom')
    '<p>This is a test!</p>'

Let's provide a custom template:

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> custom_template = os.path.join(temp_dir, 'custom-template.pt')
    >>> with open(custom_template, 'w') as file:
    ...     _ = file.write('<div>This is a custom template!</div>')

    >>> from pyams_template.template import override_template
    >>> from pyams_portal.portlets.html.skin import HTMLPortletDefaultRenderer

    >>> override_template(HTMLPortletDefaultRenderer, name='custom',
    ...                   template=custom_template, layer=IPyAMSLayer)

    >>> folder_portlets[6].settings.get_renderer().render(template_name='custom')
    '<div>This is a custom template!</div>'

We can disable the cache by defining a "preview mode" on the request:

    >>> get_annotations(request)['PREVIEW_MODE'] = True
    >>> folder_portlets[6].settings.get_renderer().render(template_name='custom')
    '<div>This is a custom template!</div>'


Rendering portal page
---------------------

Two rendering modes are available for portal pages: a *preview* mode where caching is disabled
and workflow status is ignored to always get a "fresh" preview, and a *normal* mode where
workflow status is checked and where cache can be used.

We have to register two content providers used for header and footer before rendering:

    >>> from pyams_portal.skin.page import PortalHeaderContentProvider, PortalFooterContentProvider
    >>> empty_template = os.path.join(temp_dir, 'empty-template.pt')
    >>> with open(empty_template, 'w') as file:
    ...     _ = file.write('')

    >>> override_template(PortalHeaderContentProvider, template=empty_template, layer=IPyAMSLayer)
    >>> PortalHeaderContentProvider.update = lambda x: None

    >>> override_template(PortalFooterContentProvider, template=empty_template, layer=IPyAMSLayer)
    >>> PortalFooterContentProvider.update = lambda x: None

    >>> from pyams_pagelet.interfaces import IPagelet
    >>> from pyams_portal.skin.page import PortalContextIndexPage, PortalContextPreviewPage

    >>> preview = request.registry.queryMultiAdapter((folder, request), IPagelet, name='preview.html')
    >>> preview.update()
    >>> response = preview()

    >>> response = preview()
    >>> response.status_code
    200
    >>> print(response.body.decode())
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body class="m-0 p-0">
        <div class="main container">
          <div>
            <div class="rows">
              <div class="row m-0">
                <div class="slots w-100">
                  <div class="slot float-left col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 px-0">
                    <div class="portlets ">
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p>This is a test!</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>

    >>> index = request.registry.queryMultiAdapter((folder, request), IPagelet, name='')
    >>> index.update()
    >>> response = index()
    >>> response.status_code
    200
    >>> print(response.body.decode())
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body class="m-0 p-0">
        <div class="main container">
          <div>
            <div class="rows">
              <div class="row m-0">
                <div class="slots w-100">
                  <div class="slot float-left col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 px-0">
                    <div class="portlets ">
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p>This is a test!</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>

Let's try to use several renderers on another portlet:

    >>> portlet = app_template.add_portlet(RAW_PORTLET_NAME, 'Slot 1')
    >>> portlet['portlet_id']
    7
    >>> folder_portlets = IPortalPortletsConfiguration(folder)
    >>> folder_portlets[7].settings.body = {'en': "*This* is my code"}
    >>> folder_portlets[7].settings.renderer = 'source-code'

    >>> index = request.registry.queryMultiAdapter((folder, request), IPagelet, name='')
    >>> index.update()
    >>> response = index()
    >>> print(response.body.decode())
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body class="m-0 p-0">
        <div class="main container">
          <div>
            <div class="rows">
              <div class="row m-0">
                <div class="slots w-100">
                  <div class="slot float-left col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 px-0">
                    <div class="portlets ">
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p>This is a test!</p>
                      </div>
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <div class="source"><pre><span></span><span class="linenos">1</span>*This* is my code
                          </pre></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>

    >>> folder_portlets[7].settings.renderer = 'rest'
    >>> index = request.registry.queryMultiAdapter((folder, request), IPagelet, name='')
    >>> index.update()
    >>> response = index()
    >>> print(response.body.decode())
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body class="m-0 p-0">
        <div class="main container">
          <div>
            <div class="rows">
              <div class="row m-0">
                <div class="slots w-100">
                  <div class="slot float-left col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 px-0">
                    <div class="portlets ">
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p>This is a test!</p>
                      </div>
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p><em>This</em> is my code</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>

    >>> folder_portlets[7].settings.renderer = 'markdown'
    >>> index = request.registry.queryMultiAdapter((folder, request), IPagelet, name='')
    >>> index.update()
    >>> response = index()
    >>> print(response.body.decode())
    <!DOCTYPE html>
    <html>
      <head>
      </head>
      <body class="m-0 p-0">
        <div class="main container">
          <div>
            <div class="rows">
              <div class="row m-0">
                <div class="slots w-100">
                  <div class="slot float-left col  col-12 col-sm-12 col-md-12 col-lg-12 col-xl-12 px-0">
                    <div class="portlets ">
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p>This is a test!</p>
                      </div>
                      <div class="portlet d-block d-sm-block d-md-block d-lg-block d-xl-block ">
                        <p><em>This</em> is my code</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>

Header and footer templates
---------------------------

Starting with PyAMS_portal 1.6, page header and footer can also be managed using templates in
the same way. Then, each page is using three distinct templates: header, body (which is the
default and is using unnamed adapters) and footer; each of them can be defined, shared and
configured individually.

Header and footer templates relies on specific IPortalHeaderContext and IPortalFooterContext marker interfaces.
In a classic website handled by PyAMS, only site root, inner sites and sites folders implement these interfaces;
shared contents like topics or news use header and footer templates provided by their display context.

    >>> from zope.annotation.interfaces import IAttributeAnnotatable, IAnnotations
    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> config.registry.registerAdapter(AttributeAnnotations, (IAttributeAnnotatable, ), IAnnotations)
    >>> alsoProvides(request, IAttributeAnnotatable)

    >>> from pyams_utils.request import get_annotations
    >>> config.add_request_method(get_annotations, 'annotations', reify=True)

    >>> from pyams_portal.utils import get_portal_page
    >>> page = get_portal_page(folder, page_name='header')
    >>> page
    <pyams_portal.page.PortalPage object at 0x...>
    >>> page.__parent__ is folder
    False
    >>> page.can_inherit
    False

    >>> from zope.interface import alsoProvides
    >>> from pyams_portal.interfaces import IPortalHeaderContext
    >>> alsoProvides(folder, IPortalHeaderContext)

    >>> page = get_portal_page(folder, page_name='header')
    >>> page
    <pyams_portal.page.PortalPage object at 0x...>
    >>> page.__parent__ is folder
    True
    >>> page.can_inherit
    True

    >>> request.annotations = {}

    >>> provider = PortalHeaderContentProvider()
    >>> provider.context = folder
    >>> provider.request = request
    >>> provider.page is page
    True


Tests cleanup:

    >>> tearDown()
