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

"""PyAMS_portal.zmi.presentation module

This module provides components which are used to select template in a portal context.
"""

from pyramid.events import subscriber
from zope.interface import Invalid, alsoProvides, implementer

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IDataExtractedEvent, IGroup, IInnerSubForm
from pyams_form.subform import InnerEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_portal.interfaces import IPortalContext, IPortalPage, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.zmi.interfaces import IPortalContextPresentationForm, \
    IPortalContextPresentationMenu
from pyams_portal.zmi.layout import PortalTemplateLayoutView
from pyams_skin.interfaces.viewlet import IHelpViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_viewlet.manager import viewletmanager_config
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminEditForm, FormGroupChecker
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import ISiteManagementMenu
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


TEMPLATE_INHERIT_MODE = 'inherit'
TEMPLATE_SHARED_MODE = 'shared'
TEMPLATE_LOCAL_MODE = 'local'


@viewletmanager_config(name='presentation.menu',
                       context=IPortalContext, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=20,
                       provides=IPortalContextPresentationMenu,
                       permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextPresentationMenu(NavigationMenuItem):
    """Portal context presentation menu"""

    label = _("Presentation")
    icon_class = 'far fa-object-group'
    href = '#presentation.html'


@ajax_form_config(name='presentation.html',
                  context=IPortalContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextPresentationEditForm(AdminEditForm):
    """Portal context presentation edit form"""

    title = _("Page template configuration")

    object_data = {
        'ams-reset-handler': "MyAMS.portal.presentation.resetTemplate",
        'ams-reset-keep-default': True
    }

    def __init__(self, context, request):
        super().__init__(context, request)
        if not IPortalPage(self.context).can_inherit:
            alsoProvides(self, IPortalContextPresentationForm)

    def apply_changes(self, data):
        page = IPortalPage(self.context)
        params = self.request.params
        override = True
        if page.can_inherit:
            override = params.get(
                '{}{}override_parent'.format(self.prefix, self.widgets.prefix))
        page.inherit_parent = not override
        if override:
            template_mode = params.get('template_mode')
            if template_mode == TEMPLATE_SHARED_MODE:
                page.shared_template = params.get(
                    '{}{}shared_template'.format(self.prefix, self.widgets.prefix))
                page.use_local_template = False
            elif template_mode == TEMPLATE_LOCAL_MODE:
                page.shared_template = None
                page.use_local_template = True
                template = page.local_template
                if template is not None:
                    template.css_class = params.get(
                        '{}{}css_class'.format(self.prefix, self.widgets.prefix))
        return {
            IPortalPage: ('inherit_parent', 'use_local_template', 'shared_template')
        }


@subscriber(IDataExtractedEvent, form_selector=PortalContextPresentationEditForm)
def extract_portal_context_presentation_edit_form_data(event):
    """Handle data extraction from presentation edit form"""
    form = event.form
    request = form.request
    params = request.params
    page = IPortalPage(request.context)
    override = True
    if page.can_inherit:
        override = params.get('{}{}override_parent'.format(form.prefix, form.widgets.prefix))
    if override:
        template_mode = params.get('template_mode')
        if template_mode is None:
            form.widgets.errors += (Invalid(_("You must choose between using a shared template "
                                              "or a local template if you don't inherit from "
                                              "parent template!")),)
        elif template_mode == TEMPLATE_SHARED_MODE:
            template = params.get('{}{}shared_template'.format(form.prefix, form.widgets.prefix))
            if (not template) or (template == '--NOVALUE--'):
                form.widgets.errors += (Invalid(_("You must select a template when setting "
                                                  "shared template mode!")),)


@adapter_config(name='presentation-override',
                required=(IPortalContext, IAdminLayer, PortalContextPresentationEditForm),
                provides=IGroup)
@implementer(IPortalContextPresentationForm)
class PortalContextPresentationInheritGroup(FormGroupChecker):
    """Portal context presentation inherit group"""

    def __new__(cls, context, request, parent_form):  # pylint: disable=unused-argument
        if not IPortalPage(context).can_inherit:
            return None
        return FormGroupChecker.__new__(cls)

    fields = Fields(IPortalPage).select('override_parent')
    checker_fieldname = 'override_parent'
    checker_mode = 'disable'


@adapter_config(name='presentation-template',
                required=(IPortalContext, IAdminLayer, IPortalContextPresentationForm),
                provides=IInnerSubForm)
@template_config(template='templates/presentation-template.pt', layer=IAdminLayer)
class PortalContextPresentationTemplateEditForm(InnerEditForm):
    """Portal context presentation template edit form"""

    fields = Fields(IPortalPage).select('shared_template')

    def get_content(self):
        return IPortalPage(self.context)

    @property
    def template_css_class(self):
        """Template CSS class getter"""
        result = None
        page = IPortalPage(self.context)
        template = page.local_template
        if template is not None:
            return template.css_class
        return result

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        template = self.widgets.get('shared_template')
        if template is not None:
            template.no_value_message = _("No selected template")
            template.prompt_message = _("Please select template...")
            template.placeholder = _("Please select template...")
            template.object_data = {
                'ams-change-handler': 'MyAMS.portal.presentation.setSharedTemplate'
            }
            alsoProvides(template, IObjectData)


@viewlet_config(name='presentation-template.help',
                context=IPortalContext, layer=IAdminLayer,
                view=PortalContextPresentationEditForm, manager=IHelpViewletManager, weight=10)
class PortalContextPresentationEditFormHelp(AlertMessage):
    """Portal context presentation edit form help"""

    status = 'info'
    _message = _("If you select a shared template or choose to inherit from parent "
                 "configuration, you can adjust settings of each portlet but can't change "
                 "page configuration.\n"
                 "If you choose to use a local template, it's configuration will only be "
                 "reusable in sub-levels which will choose to inherit from it.")


#
# Portal context template settings components
#

@viewlet_config(name='template-layout.menu',
                context=IPortalContext, layer=IAdminLayer,
                manager=IPortalContextPresentationMenu, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextTemplateLayoutMenu(NavigationMenuItem):
    """Portal context template layout menu"""

    label = _("Page layout")
    href = '#template-layout.html'


@pagelet_config(name='template-layout.html',
                context=IPortalContext, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextTemplateLayoutView(PortalTemplateLayoutView):
    """Portal context template layout view"""

    def get_template(self):
        return IPortalPage(self.context).template

    @property
    def can_change(self):
        return IPortalPage(self.context).use_local_template
