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

"""PyAMS_portal.portlets.carousel.zmi module

Management components for carousel portlet.
"""

from pyramid.view import view_config
from zope.interface import Interface

from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer
from pyams_i18n.interfaces import II18n
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortletPreviewer, MANAGE_TEMPLATE_PERMISSION
from pyams_portal.portlets.carousel import ICarouselImage, ICarouselPortletSettings
from pyams_portal.zmi import PortletPreviewer
from pyams_portal.zmi.portlet import PortletConfigurationEditForm
from pyams_skin.interfaces.viewlet import IContentSuffixViewletManager
from pyams_skin.viewlet.actions import ContextAction
from pyams_table.interfaces import IColumn, IValues
from pyams_template.template import template_config
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.data import ObjectDataManagerMixin
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.helper.container import delete_container_element, switch_element_attribute
from pyams_zmi.helper.event import get_json_table_row_add_callback, \
    get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import IconColumn, InnerTableAdminView, JsActionColumn, NameColumn, \
    ReorderColumn, Table, TableElementEditor, TrashColumn, get_ordered_data_attributes
from pyams_zmi.utils import get_object_label


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class CarouselItemsTable(Table):
    """Carousel items table"""

    @property
    def data_attributes(self):
        attributes = super().data_attributes
        container = ICarouselPortletSettings(self.context)
        get_ordered_data_attributes(attributes, container, self.request)
        return attributes

    display_if_empty = True


@adapter_config(required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IValues)
class CarouselItemsTableValues(ContextRequestViewAdapter):
    """Carousel items table values adapter"""

    @property
    def values(self):
        """Carousel table values getter"""
        yield from self.context.values()


@adapter_config(name='reorder',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableReorderColumn(ReorderColumn):
    """Carousel items table reorder column"""


@view_config(name='reorder.json',
             context=ICarouselPortletSettings, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=MANAGE_TEMPLATE_PERMISSION)
def reorder_cards_table(request):
    """Reorder carousel items table"""
    order = request.params.get('order').split(';')
    request.context.updateOrder(order)
    return {
        'status': 'success',
        'closeForm': False
    }


@adapter_config(name='visible',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableVisibleColumn(ObjectDataManagerMixin, JsActionColumn):
    """Carousel items table visible column"""

    hint = _("Click icon to show or hide item")

    href = 'MyAMS.container.switchElementAttribute'
    modal_target = False

    object_data = {
        'ams-modules': 'container',
        'ams-update-target': 'switch-visible-item.json',
        'ams-attribute-name': 'visible',
        'ams-icon-on': 'far fa-eye',
        'ams-icon-off': 'far fa-eye-slash'
    }

    weight = 1

    def get_icon_class(self, item):
        """Icon class getter"""
        return 'far fa-eye' if item.visible else 'far fa-eye-slash'


@view_config(name='switch-visible-item.json',
             context=ICarouselPortletSettings, request_type=IPyAMSLayer,
             renderer='json', xhr=True)
def switch_visible_item(request):
    """Switch visible item"""
    return switch_element_attribute(request)


@adapter_config(name='title',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableTitleColumn(NameColumn):
    """Carousel items table name column"""

    i18n_header = _("Title")


@adapter_config(name='lead',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableLeadColumn(NameColumn):
    """Carousel items table lead column"""

    i18n_header = _("Lead")
    weight = 20

    def get_value(self, obj):
        return II18n(obj).query_attribute('lead', request=self.request) or '--'


@adapter_config(name='illustration',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableIllustrationColumn(IconColumn):
    """Carousel items table illustration column"""

    weight = 90
    icon_class = 'far fa-image text-muted'
    hint = _("Illustration")

    checker = lambda self, x: bool(x.illustration and x.illustration.data)


@adapter_config(name='trash',
                required=(ICarouselPortletSettings, IAdminLayer, CarouselItemsTable),
                provides=IColumn)
class CarouselItemsTableTrashColumn(TrashColumn):
    """Carousel items table trash column"""


@view_config(name='delete-element.json',
             context=ICarouselPortletSettings, request_type=IPyAMSLayer,
             renderer='json', xhr=True,
             permission=MANAGE_TEMPLATE_PERMISSION)
def delete_item(request):
    """Delete carousel item"""
    return delete_container_element(request)


@viewlet_config(name='carousel-items-table',
                context=ICarouselPortletSettings, layer=IAdminLayer,
                view=PortletConfigurationEditForm,
                manager=IContentSuffixViewletManager, weight=10)
class CarouselItemsTableView(InnerTableAdminView):
    """Carousel items table view"""

    table_class = CarouselItemsTable
    table_label = _("List of carousel items")


@adapter_config(required=(Interface, IPyAMSLayer, Interface, ICarouselPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/carousel-preview.pt', layer=IPyAMSLayer)
class CarouselPortletPreviewer(PortletPreviewer):
    """Carousel portlet previewer"""


#
# Carousel items forms
#

@viewlet_config(name='add-image.menu',
                context=ICarouselPortletSettings, layer=IAdminLayer, view=CarouselItemsTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_TEMPLATE_PERMISSION)
class CarouselImageAddMenu(ContextAction):
    """Carousel image add menu"""

    status = 'success'
    icon_class = 'fas fa-plus'
    label = _("Add image")

    href = 'add-image.html'
    modal_target = True


@ajax_form_config(name='add-image.html',
                  context=ICarouselPortletSettings, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class CarouselImageAddForm(AdminModalAddForm):
    """Carousel image add form"""

    @property
    def title(self):
        translate = self.request.localizer.translate
        portlet = self.context.configuration.get_portlet()
        return '<small>{}</small><br />{}'.format(
            translate(_("Portlet configuration: « {} »")).format(portlet.label),
            translate(_("Add new image"))
        )

    legend = _("New image properties")
    modal_class = 'modal-xl'

    fields = Fields(ICarouselImage).omit('__name__', '__parent__', 'visible')
    content_factory = ICarouselImage

    def add(self, obj):
        self.context.append(obj)


@adapter_config(required=(ICarouselPortletSettings, IAdminLayer, CarouselImageAddForm),
                provides=IAJAXFormRenderer)
class CarouselImageAddFormRenderer(ContextRequestViewAdapter):
    """Carousel image add form renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'status': 'success',
            'callbacks': [
                get_json_table_row_add_callback(self.context, self.request,
                                                CarouselItemsTable, changes)
            ]
        }


@adapter_config(required=(ICarouselImage, IAdminLayer, Interface),
                provides=ITableElementEditor)
class CarouselImageElementEditor(TableElementEditor):
    """Carousel image element editor"""


@ajax_form_config(name='properties.html',
                  context=ICarouselImage, layer=IPyAMSLayer,
                  permission=MANAGE_TEMPLATE_PERMISSION)
class CarouselImageEditForm(AdminModalEditForm):
    """Carousel image properties edit form"""

    @property
    def title(self):
        translate = self.request.localizer.translate
        portlet = self.context.__parent__.configuration.get_portlet()
        return '<small>{}</small><br />{}'.format(
            translate(_("Portlet configuration: « {} »")).format(portlet.label),
            translate(_("Image: {}")).format(get_object_label(self.context, self.request, self))
        )

    legend = _("Carousel image properties")
    modal_class = 'modal-xl'

    fields = Fields(ICarouselImage).omit('__name__', '__parent__', 'visible')


@adapter_config(required=(ICarouselImage, IAdminLayer, CarouselImageEditForm),
                provides=IAJAXFormRenderer)
class CarouselImageEditFormRenderer(ContextRequestViewAdapter):
    """Carousel image edit form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(self.context.__parent__, self.request,
                                                    CarouselItemsTable, self.context)
            ]
        }
