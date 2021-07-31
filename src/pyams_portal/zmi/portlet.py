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

"""PyAMS_portal.zmi.portlet module

This module defines portlets management components.
"""

import json

from pyramid.exceptions import NotFound
from pyramid.renderers import render
from pyramid.view import view_config
from zope.interface import Interface, alsoProvides, implementer

from pyams_form.ajax import AJAXFormRenderer, ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import HIDDEN_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IGroup, IInnerSubForm
from pyams_form.subform import InnerEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalContext, IPortalPage, IPortalPortletsConfiguration, \
    IPortalTemplate, IPortalTemplateConfiguration, IPortletAddingInfo, IPortletConfiguration, \
    IPortletPreviewer, IPortletRendererSettings, IPortletSettings, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.page import check_local_template
from pyams_portal.portlet import LOGGER
from pyams_portal.skin import PORTLETS_CACHE_NAME, PORTLETS_CACHE_NAMESPACE, PORTLETS_CACHE_REGION
from pyams_portal.zmi.interfaces import IPortletConfigurationEditor
from pyams_portal.zmi.layout import PortalTemplateLayoutView
from pyams_portal.zmi.widget import PortletRendererFieldWidget
from pyams_skin.interfaces.viewlet import IHeaderViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_skin.viewlet.menu import MenuDivider, MenuItem
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.cache import get_cache
from pyams_utils.dict import merge_dict
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm, FormGroupChecker
from pyams_zmi.helper.event import get_json_widget_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextAddingsViewletManager
from pyams_zmi.utils import get_object_label


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


@viewlet_config(name='add-template-portlet.divider',
                context=IPortalTemplate, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=49)
class PortalTemplatePortletAddMenuDivider(MenuDivider):
    """Portal template portlet add menu divider"""


@viewlet_config(name='add-template-portlet.divider',
                context=IPortalContext, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=49)
class PortalContextPortletAddMenuDivider(MenuDivider):
    """Portal context portlet add menu divider"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        page = IPortalPage(context)
        if not page.use_local_template:
            return None
        return MenuDivider.__new__(cls)


@viewlet_config(name='add-template-portlet.menu',
                context=IPortalTemplate, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=50)
class PortalTemplatePortletAddMenu(MenuItem):
    """Portal template slot add menu"""

    label = _("Add portlet...")
    icon_class = 'far fa-window-restore'

    href = 'add-template-portlet.html'
    modal_target = True


@viewlet_config(name='add-template-portlet.menu',
                context=IPortalContext, layer=IAdminLayer,
                view=PortalTemplateLayoutView, manager=IContextAddingsViewletManager,
                permission=MANAGE_TEMPLATE_PERMISSION, weight=50)
class PortalContextTemplatePortletAddMenu(PortalTemplatePortletAddMenu):
    """Portal context template portlet add menu"""

    def __new__(cls, context, request, view, manager):  # pylint: disable=unused-argument
        page = IPortalPage(context)
        if not page.use_local_template:
            return None
        return PortalTemplatePortletAddMenu.__new__(cls)


@ajax_form_config(name='add-template-portlet.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@ajax_form_config(name='add-template-portlet.html',
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatePortletAddForm(AdminModalAddForm):  # pylint: disable=abstract-method
    """Portal template portlet add form"""

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        if IPortalTemplate.providedBy(self.context):
            return translate(_("« {} »  portal template")).format(self.context.name)
        return '<small>{}</small><br />{}'.format(
            get_object_label(self.context, self.request, self),
            translate(_("Local template")))

    legend = _("Add template portlet")

    fields = Fields(IPortletAddingInfo)

    def __init__(self, context, request):
        check_local_template(context)
        super().__init__(context, request)

    def create_and_add(self, data):
        data = data.get(self, {})
        return self.create(data)

    def create(self, data):
        config = IPortalTemplateConfiguration(self.context)
        return config.add_portlet(data.get('portlet_name'), data.get('slot_name'))


@adapter_config(required=(IPortalTemplate, IAdminLayer, PortalTemplatePortletAddForm),
                provides=IAJAXFormRenderer)
@adapter_config(required=(IPortalContext, IAdminLayer, PortalTemplatePortletAddForm),
                provides=IAJAXFormRenderer)
class PortalTemplatePortletAddFormRenderer(ContextRequestViewAdapter):
    """Portal template portlet add form JSON renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if changes is None:
            return None
        portlets_config = IPortalPortletsConfiguration(self.context)
        config = portlets_config.get_portlet_configuration(changes['portlet_id'])
        settings = config.settings
        previewer = self.request.registry.queryMultiAdapter(
            (self.context, self.request, self, settings), IPortletPreviewer)
        if previewer is not None:
            previewer.update()
            changes['preview'] = render('templates/portlet-preview.pt', {
                'config': config,
                'can_change': True,
                'can_delete': IPortalTemplate.providedBy(self.context),
                'label': config.get_portlet().label,
                'portlet': previewer.render(),
                'visible': settings.visible
            }, request=self.request)
        return {
            'status': 'success',
            'callback': 'MyAMS.portal.template.addPortletCallback',
            'options': changes
        }


@view_config(name='drop-template-portlet.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='drop-template-portlet.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def drop_template_portlet(request):
    """Drop portlet icon to slot"""
    context = request.context
    check_local_template(context)
    portlet_name = request.params.get('portlet_name')
    slot_name = request.params.get('slot_name')
    tmpl_config = IPortalTemplateConfiguration(context)
    changes = tmpl_config.add_portlet(portlet_name, slot_name)
    portlets_config = IPortalPortletsConfiguration(context)
    config = portlets_config.get_portlet_configuration(changes['portlet_id'])
    settings = config.settings
    previewer = request.registry.queryMultiAdapter((context, request, None, settings),
                                                   IPortletPreviewer)
    if previewer is not None:
        previewer.update()
        changes['preview'] = render('templates/portlet-preview.pt', {
            'config': config,
            'can_change': True,
            'can_delete': IPortalTemplate.providedBy(config.__parent__),
            'label': config.get_portlet().label,
            'portlet': previewer.render()
        }, request=request)
    return {
        'status': 'callback',
        'close_form': False,
        'callback': 'MyAMS.portal.template.addPortletCallback',
        'options': changes
    }


@ajax_form_config(name='portlet-properties.html',
                  context=IPortalTemplate, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
@ajax_form_config(name='portlet-properties.html',
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalTemplatePortletEditForm(AdminModalEditForm):
    """Portal template portlet properties edit form"""

    modal_class = 'modal-xl'

    portlet = None

    def __init__(self, context, request):
        super().__init__(context, request)
        self.initial_context = context
        portlet_id = int(request.params.get('{}widgets.portlet_id'.format(self.prefix)))
        self.portlet_config = portlet_config = IPortalPortletsConfiguration(self.context) \
            .get_portlet_configuration(portlet_id)
        if portlet_config is None:
            raise NotFound()
        self.portlet = portlet_config.get_portlet()
        self.context = portlet_config.editor_settings
        if not portlet_config.can_inherit:
            alsoProvides(self, IPortletConfigurationEditor)

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        if IPortalTemplate.providedBy(self.context):
            title = translate(_("« {} »  portal template")).format(self.context.name)
        else:
            context = get_parent(self.context, IPortalContext)
            page = IPortalPage(context)
            if page.use_shared_template:
                title = translate(_("« {} » shared template")).format(page.template.name)
            else:
                title = translate(_("Local template"))
            if page.inherit_parent:
                title = translate(_("{} (inherited from parent)")).format(title)
            if IPortalContext.providedBy(self.initial_context):
                title = '{} - {}'.format(
                    get_object_label(self.initial_context, self.request, self), title)
        return '<small>{}</small><br />{}'.format(
            title,
            translate(_("Portlet configuration: « {} »")).format(translate(self.portlet.label)))

    @property
    def fields(self):
        """Fields getter"""
        return Fields(IPortletConfiguration).select('portlet_id')

    @property
    def settings_factory(self):
        """Settings factory getter"""
        return self.portlet.settings_factory

    def get_ajax_handler(self):
        """AJAX form handler getter"""
        return absolute_url(self.initial_context, self.request, self.ajax_form_handler)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        portlet_id = self.widgets['portlet_id']
        if portlet_id is not None:
            portlet_id.mode = HIDDEN_MODE


@adapter_config(required=(Interface, IAdminLayer, PortalTemplatePortletEditForm),
                provides=IAJAXFormRenderer)
class PortalTemplatePortletEditFormRenderer(AJAXFormRenderer):
    """Portal template portlet edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        config = IPortletConfiguration(self.form.context)
        settings = config.settings
        previewer = self.request.registry.queryMultiAdapter(
            (self.context, self.request, self.form, settings), IPortletPreviewer)
        result = {
            'status': 'success',
            'callbacks': [{
                'callback': 'MyAMS.portal.template.editPortletCallback',
                'options': {
                    'portlet_id': config.portlet_id,
                    'inherit_parent': config.inherit_parent
                }
            }]
        }
        if 'autosubmit' in self.request.params:
            result['closeForm'] = False
        if previewer is not None:
            previewer.update()
            result['callbacks'][0]['options']['preview'] = render('templates/portlet-preview.pt', {
                'config': config,
                'can_change': True,
                'can_delete': IPortalTemplate.providedBy(config.__parent__),
                'label': config.get_portlet().label,
                'portlet': previewer.render()
            }, request=self.request)
        output = super().render(changes)
        if output:
            merge_dict(output, result)
        return result


@adapter_config(name='inherit',
                required=(Interface, IAdminLayer, PortalTemplatePortletEditForm),
                provides=IGroup)
@implementer(IPortletConfigurationEditor)
class PortletConfigurationInheritGroup(FormGroupChecker):
    """Portlet configuration inherit group"""

    def __new__(cls, context, request, parent_form):  # pylint: disable=unused-argument
        if not parent_form.portlet_config.can_inherit:
            return None
        return FormGroupChecker.__new__(cls)

    fields = Fields(IPortletConfiguration).select('override_parent')
    checker_fieldname = 'override_parent'
    checker_mode = 'disable'

    object_data = {
        'ams-change-handler': 'MyAMS.portal.template.submitPortletEditForm'
    }

    @property
    def settings_factory(self):
        """Settings factory getter"""
        return self.parent_form.portlet.settings_factory


@viewlet_config(name='help',
                context=Interface, layer=IAdminLayer, view=PortletConfigurationInheritGroup,
                manager=IHeaderViewletManager, weight=10)
class PortalTemplatePortletEditFormHelp(AlertMessage):
    """Portal template portlet edit form help"""

    status = 'warning'
    _message = _("WARNING: portlet configuration is saved immediately when inherit mode is "
                 "changed!!")


@adapter_config(name='configuration',
                required=(Interface, IAdminLayer, IPortletConfigurationEditor),
                provides=IInnerSubForm)
class PortletConfigurationEditForm(InnerEditForm):
    """Portlet configuration edit form"""

    @property
    def legend(self):
        """Legend getter"""
        if IGroup.providedBy(self.parent_form):
            return None
        return _("Portlet settings")

    border_class = ''

    @property
    def fields(self):
        """Form fields getter"""
        factory = self.parent_form.settings_factory
        fields = Fields(factory).omit('__name__', 'renderer') + Fields(factory).select('renderer')
        fields['renderer'].widget_factory = PortletRendererFieldWidget
        return fields


@adapter_config(required=(Interface, IAdminLayer, PortletConfigurationEditForm),
                provides=IAJAXFormRenderer)
class PortletConfigurationEditFormRenderer(AJAXFormRenderer):
    """Portlet configuration edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        # clear portlets cache on update
        LOGGER.debug("Clearing portlets cache...")
        portlets_cache = get_cache(PORTLETS_CACHE_NAME,
                                   PORTLETS_CACHE_REGION,
                                   PORTLETS_CACHE_NAMESPACE)
        portlets_cache.clear()
        # return notice on renderer update
        if 'renderer' in changes.get(IPortletSettings, ()):
            result = {}
            renderer = self.context.get_renderer(self.request)
            if (renderer is not None) and \
                    (renderer.target_interface is None) and \
                    (renderer.settings_interface is not None):
                translate = self.request.localizer.translate
                result.update({
                    'closeForm': False,
                    'smallbox': {
                        'status': 'info',
                        'timeout': 5000,
                        'message': translate(_("You changed selected portlet renderer. "
                                               "Don't omit to check new renderer settings..."))
                    }
                })
                result.setdefault('callbacks', []).append(
                    get_json_widget_refresh_callback(self.form, 'renderer', self.request)
                )
            return result
        return None


@view_config(name='set-template-portlet-order.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='set-template-portlet-order.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def set_template_portlet_order(request):
    """Set template portlet order"""
    context = request.context
    check_local_template(context)
    order = json.loads(request.params.get('order'))
    order['from'] = int(order['from'])
    order['to']['portlet_ids'] = list(map(int, order['to']['portlet_ids']))
    IPortalTemplateConfiguration(context).set_portlet_order(order)
    return {'status': 'success'}


@view_config(name='delete-template-portlet.json',
             context=IPortalTemplate, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
@view_config(name='delete-template-portlet.json',
             context=IPortalContext, request_type=IPyAMSLayer,
             permission=MANAGE_TEMPLATE_PERMISSION, renderer='json', xhr=True)
def delete_template_portlet(request):
    """Delete template portlet"""
    context = request.context
    check_local_template(context)
    config = IPortalTemplateConfiguration(context)
    config.delete_portlet(int(request.params.get('portlet_id')))
    return {'status': 'success'}


#
# Portlet renderer settings edit form
#

@ajax_form_config(name='renderer-settings.html',
                  context=IPortletSettings, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortletRendererSettingsEditForm(AdminModalEditForm):
    """Portlet renderer settings edit form"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.renderer = self.context.get_renderer(request)

    @property
    def title(self):
        """Title getter"""
        translate = self.request.localizer.translate
        return translate(_("<small>Portlet: {portlet}</small><br />« {renderer} » renderer")) \
            .format(portlet=translate(self.renderer.portlet.label),
                    renderer=translate(self.renderer.label))

    legend = _("Edit renderer settings")
    modal_class = 'modal-xl'

    @property
    def fields(self):
        """Form fields getter"""
        return Fields(self.renderer.settings_interface or Interface)

    def get_content(self):
        return IPortletRendererSettings(self.context)


@adapter_config(required=(Interface, IAdminLayer, PortletRendererSettingsEditForm),
                provides=IAJAXFormRenderer)
class PortletRendererSettingsEditFormRenderer(ContextRequestViewAdapter):
    """Portlet renderer settings edit form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        # clear portlets cache on update
        LOGGER.debug("Clearing portlets cache...")
        portlets_cache = get_cache(PORTLETS_CACHE_NAME,
                                   PORTLETS_CACHE_REGION,
                                   PORTLETS_CACHE_NAMESPACE)
        portlets_cache.clear()
        return {
            'status': 'success',
            'message': self.request.localizer.translate(self.view.success_message)
        }
