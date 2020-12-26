#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_pagelet.pagelet module

This module provides the core pagelet implementation, and a "pagelet_config" decorator which
can be use to register pagelets instead of ZCML directives.
"""

import logging

import venusian
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.interfaces import IRequest
from pyramid.response import Response
from zope.interface import Interface, implementer

from pyams_pagelet.interfaces import IPagelet, IPageletRenderer, PageletCreatedEvent
from pyams_template.template import get_content_template, get_layout_template
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'

LOGGER = logging.getLogger('PyAMS (pagelet)')

REDIRECT_STATUS_CODES = (301, 302, 303)


@implementer(IPagelet)
class Pagelet:
    """Content provider with layout support"""

    template = get_content_template()
    layout = get_layout_template()

    permission = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        if self.permission and not request.has_permission(self.permission):
            raise HTTPUnauthorized('You are not authorized to access the page called `%s`.' %
                                   request.view_name)

    def update(self):
        """See `zope.contentprovider.interfaces.IContentProvider`"""
        annotations = getattr(self.request, 'annotations', None)
        if annotations is not None:
            annotations['view'] = self

    def render(self):
        """See `zope.contentprovider.interfaces.IContentProvider`"""
        return self.template()  # pylint: disable=not-callable

    def __call__(self, **kwargs):
        """Call update and return layout template"""
        self.request.registry.notify(PageletCreatedEvent(self))
        self.update()

        # Don't render anything if we are doing a redirect
        request = self.request
        if request.response.status_code in REDIRECT_STATUS_CODES:
            return Response('')

        return Response(self.layout(**kwargs))  # pylint: disable=not-callable


@adapter_config(name='pagelet',
                required=(Interface, IRequest, IPagelet),
                provides=IPageletRenderer)
class PageletRenderer:
    """Pagelet renderer"""

    def __init__(self, context, request, pagelet):
        self.__updated = False
        self.__parent__ = pagelet
        self.context = context
        self.request = request

    def update(self):
        """See `zope.contentprovider.interfaces.IContentProvider`"""

    def render(self):
        """See `zope.contentprovider.interfaces.IContentProvider`"""
        return self.__parent__.render()


class pagelet_config:  # pylint: disable=invalid-name
    """Function or class decorator used to declare a pagelet"""

    venusian = venusian  # for testing injection

    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings.pop('for_')
        if 'layer' in settings:
            settings['request_type'] = settings.pop('layer')
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, obj):  # pylint: disable=unused-argument
            """Venusian decorator callback"""
            cdict = {
                '__name__': settings.get('name'),
                '__module__': obj.__module__,
                'permission': settings.get('permission')
            }
            new_class = type(obj.__name__, (obj, Pagelet), cdict)

            LOGGER.debug('Registering pagelet view "{0}" for {1} ({2})'.format(
                settings.get('name'), str(settings.get('context', Interface)), str(new_class)))

            config = context.config.with_package(info.module)  # pylint: disable=no-member
            registry = settings.get('registry')
            if registry is None:
                registry = config.registry
            registry.registerAdapter(new_class,
                                     (settings.get('context', Interface),
                                      settings.get('request_type', IRequest)),
                                     IPagelet, settings.get('name'))

            if 'registry' in settings:
                settings.pop('registry')
            if 'venusian' in settings:
                settings.pop('venusian')
            config.add_view(view=new_class, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyams_pagelet',
                                    depth=depth + 1)

        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped
