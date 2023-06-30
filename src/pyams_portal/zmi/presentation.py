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
from pyams_portal.interfaces import IPortalContext, IPortalFooterContext, IPortalHeaderContext, \
    IPortalPage, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.utils import get_portal_page
from pyams_portal.zmi.interfaces import IPortalContextPresentationForm, \
    IPortalContextPresentationMenu, IPortalContextHeaderPresentationMenu, IPortalContextFooterPresentationMenu
from pyams_portal.zmi.layout import PortalTemplateLayoutView
from pyams_skin.interfaces.viewlet import IHelpViewletManager
from pyams_skin.viewlet.help import AlertMessage
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.interfaces.form import NO_VALUE_STRING
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

    page_name = ''
    object_data = {
        'ams-reset-handler': "MyAMS.portal.presentation.resetTemplate",
        'ams-reset-keep-default': True
    }

    def __init__(self, context, request):
        super().__init__(context, request)
        page = self.get_content()
        if not page.can_inherit:
            alsoProvides(self, IPortalContextPresentationForm)

    def get_content(self):
        """Form content getter"""
        return get_portal_page(self.context, page_name=self.page_name)

    def apply_changes(self, data):
        page = self.get_content()
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


#
# Header presentation
#

@viewletmanager_config(name='header-presentation.menu',
                       context=IPortalHeaderContext, layer=IAdminLayer,
                       manager=IPortalContextPresentationMenu, weight=20,
                       provides=IPortalContextHeaderPresentationMenu,
                       permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextHeaderPresentationMenu(NavigationMenuItem):
    """Portal context header presentation menu"""

    label = _("Header presentation")
    icon_class = 'fas fa-arrows-up-to-line'
    href = '#header-presentation.html'


@ajax_form_config(name='header-presentation.html',
                  context=IPortalHeaderContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextHeaderPresentationEditForm(PortalContextPresentationEditForm):
    """Portal context header presentation edit form"""

    title = _("Page header template configuration")

    page_name = 'header'


#
# Footer presentation
#

@viewletmanager_config(name='footer-presentation.menu',
                       context=IPortalFooterContext, layer=IAdminLayer,
                       manager=IPortalContextPresentationMenu, weight=20,
                       provides=IPortalContextFooterPresentationMenu,
                       permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextFooterPresentationMenu(NavigationMenuItem):
    """Portal context footer presentation menu"""

    label = _("Footer presentation")
    icon_class = 'fas fa-arrows-down-to-line'
    href = '#footer-presentation.html'


@ajax_form_config(name='footer-presentation.html',
                  context=IPortalFooterContext, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextFooterPresentationEditForm(PortalContextPresentationEditForm):
    """Portal context footer presentation edit form"""

    title = _("Page footer template configuration")

    page_name = 'footer'


#
# Presentation management form
#

@subscriber(IDataExtractedEvent, form_selector=PortalContextPresentationEditForm)
def extract_portal_context_presentation_edit_form_data(event):
    """Handle data extraction from presentation edit form"""
    form = event.form
    request = form.request
    params = request.params
    override = True
    page = form.get_content()
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
            if (not template) or (template == NO_VALUE_STRING):
                form.widgets.errors += (Invalid(_("You must select a template when setting "
                                                  "shared template mode!")),)


@adapter_config(name='presentation-override',
                required=(IPortalContext, IAdminLayer, PortalContextPresentationEditForm),
                provides=IGroup)
@implementer(IPortalContextPresentationForm)
class PortalContextPresentationInheritGroup(FormGroupChecker):
    """Portal context presentation inherit group"""

    def __new__(cls, context, request, parent_form):  # pylint: disable=unused-argument
        page = parent_form.get_content()
        if not page.can_inherit:
            return None
        return FormGroupChecker.__new__(cls)

    fields = Fields(IPortalPage).select('override_parent')
    checker_fieldname = 'override_parent'
    checker_mode = 'disable'

    @property
    def page_name(self):
        """Portal page name getter"""
        return self.parent_form.page_name


@adapter_config(name='presentation-template',
                required=(IPortalContext, IAdminLayer, IPortalContextPresentationForm),
                provides=IInnerSubForm)
@template_config(template='templates/presentation-template.pt', layer=IAdminLayer)
class PortalContextPresentationTemplateEditForm(InnerEditForm):
    """Portal context presentation template edit form"""

    fields = Fields(IPortalPage).select('shared_template')

    def get_content(self):
        return self.parent_form.get_content()

    @property
    def template_css_class(self):
        """Template CSS class getter"""
        result = None
        page = self.get_content()
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

    page_name = ''

    def __new__(cls, context, request, view, manager):
        page = get_portal_page(context, page_name=cls.page_name)
        if page.template is None:
            return None
        return NavigationMenuItem.__new__(cls)


@pagelet_config(name='template-layout.html',
                context=IPortalContext, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextTemplateLayoutView(PortalTemplateLayoutView):
    """Portal context template layout view"""

    def get_template(self):
        page = self.get_portal_page()
        return page.template

    @property
    def can_change(self):
        page = self.get_portal_page()
        return page.use_local_template


@viewlet_config(name='header-template-layout.menu',
                context=IPortalContext, layer=IAdminLayer,
                manager=IPortalContextHeaderPresentationMenu, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextHeaderTemplateLayoutMenu(PortalContextTemplateLayoutMenu):
    """Portal context header template layout menu"""

    label = _("Header layout")
    href = '#header-template-layout.html'

    page_name = 'header'


@pagelet_config(name='header-template-layout.html',
                context=IPortalContext, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextHeaderTemplateLayoutView(PortalContextTemplateLayoutView):
    """Portal context header template layout view"""

    page_name = 'header'


@viewlet_config(name='footer-template-layout.menu',
                context=IPortalContext, layer=IAdminLayer,
                manager=IPortalContextFooterPresentationMenu, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextFooterTemplateLayoutMenu(PortalContextTemplateLayoutMenu):
    """Portal context footer template layout menu"""

    label = _("Footer layout")
    href = '#footer-template-layout.html'

    page_name = 'footer'


@pagelet_config(name='footer-template-layout.html',
                context=IPortalContext, layer=IPyAMSLayer,
                permission=MANAGE_TEMPLATE_PERMISSION)
class PortalContextFooterTemplateLayoutView(PortalContextTemplateLayoutView):
    """Portal context footer template layout view"""

    page_name = 'footer'
