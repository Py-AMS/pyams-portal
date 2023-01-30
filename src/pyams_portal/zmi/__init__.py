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

"""PyAMS_portal.zmi main module

This module defines base ZMI components.
"""

from fanstatic import Library, Resource
from pyramid.renderers import render
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import IBool

from pyams_i18n.schema import II18nField
from pyams_layer.interfaces import IPyAMSLayer
from pyams_portal.interfaces import IPortalTemplate, IPortalTemplateConfiguration, \
    IPortletPreviewer, IPortletSettings
from pyams_portal.skin import PortletContentProvider
from pyams_skin.interfaces import BOOTSTRAP_DEVICES_ICONS, BOOTSTRAP_SIZES
from pyams_template.template import template_config
from pyams_utils.adapter import adapter_config
from pyams_utils.text import text_to_html

__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


library = Library('pyams_portal', 'resources')


layout_css = Resource(library, 'css/layout.css',
                      minified='css/layout.min.css')

layout_js = Resource(library, 'js/layout.js',
                     minified='js/layout.min.js',
                     depends=(layout_css,))


#
# Portlet preview
#

PREVIEW_PREFIX = '''<div class="text-info text-truncate border-bottom mb-1">
    <small>{label}</small>
    {renderer}
    <span class="float-right">{visibility}</span>
</div>'''

VISIBLE_ICON = '<i class="fa fa-fw {icon} hint" title="{title}"></i>'

HIDDEN_ICON = '<i class="fa fa-fw {icon} text-warning hint" title="{title}"></i>'


def get_visibility_icons(settings, translate):
    """Visibility icons getter"""
    for size, value in settings.devices_visibility.items():
        if value:
            yield VISIBLE_ICON.format(icon=BOOTSTRAP_DEVICES_ICONS.get(size),
                                      title=translate(BOOTSTRAP_SIZES.get(size)))
        else:
            yield HIDDEN_ICON.format(icon=BOOTSTRAP_DEVICES_ICONS.get(size),
                                     title=translate(BOOTSTRAP_SIZES.get(size)))


@adapter_config(required=(Interface, IPyAMSLayer, Interface, IPortletSettings),
                provides=IPortletPreviewer)
@template_config(template='templates/empty.pt', layer=IPyAMSLayer)
class PortletPreviewer(PortletContentProvider):
    """Portlet previewer adapter"""

    @property
    def slot_configuration(self):
        """Slot configuration getter"""
        if IPortalTemplate.providedBy(self.context):
            template = self.context
        else:
            template = self.settings.configuration.parent
        config = IPortalTemplateConfiguration(template)
        _slot_id, slot_name = config.get_portlet_slot(self.settings.configuration.portlet_id)
        return config.get_slot_configuration(slot_name)

    def render(self, template_name=''):
        """Preview portlet content"""
        if self.settings.renderer == 'hidden':
            return render('templates/portlet-hidden.pt', {}, request=self.request)
        translate = self.request.localizer.translate
        renderer = self.settings.get_renderer()
        result = PREVIEW_PREFIX.format(
            label=translate(_("Renderer:")),
            renderer=translate(renderer.label if renderer is not None
                               else _("!! MISSING RENDERER !!")),
            visibility=' '.join(get_visibility_icons(self.settings, translate)))
        result += super().render(template_name)
        return result

    def get_setting(self, source, name, renderer=None, visible=True, icon=None):  # pylint: disable=too-many-arguments
        """Setting value renderer"""
        localizer = self.request.localizer
        translate = localizer.translate
        field = getFields(self.portlet.settings_factory)[name]
        label = translate(field.title)
        value = field.bind(source).get(source)
        if value and II18nField.providedBy(field):
            field = field.value_type
            value = value.get(localizer.locale_name)
        if value is None:
            return render('templates/setting-none-preview.pt', {
                'label': label,
                'visible': visible,
                'icon': icon
            })
        if IBool.providedBy(field):
            return render('templates/setting-bool-preview.pt', {
                'label': label,
                'checked': bool(value)
            })
        if renderer is not None:
            value = text_to_html(value, renderer, field=field, context=source)
        return render('templates/setting-preview.pt', {
            'label': label,
            'value': value,
            'visible': visible,
            'icon': icon
        })
