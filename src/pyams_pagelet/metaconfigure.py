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

"""PyAMS_pagelet.metaconfigure module

This module provides handlers for ZCML directives.
"""

from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IRequest
from pyramid_zcml import with_context
from zope.component import zcml
from zope.component.interface import provideInterface
from zope.interface import Interface, classImplements

from pyams_pagelet.interfaces import IPagelet
from pyams_pagelet.pagelet import Pagelet


def PageletDirective(_context, name, view,
                     context=Interface,
                     permission=None,
                     layer=IRequest,
                     **kwargs):
    # pylint: disable=invalid-name
    """Pagelet ZCML directive"""

    if not view:
        raise ConfigurationError("You must specify a view class or interface")
    cdict = {
        '__name__': name,
        'permission': permission
    }
    cdict.update(kwargs)
    new_class = type(view.__name__, (view, Pagelet), cdict)

    classImplements(new_class, IPagelet)

    # Register the interfaces
    _handle_for(_context, context)

    # Register pagelet
    _context.action(discriminator=('pagelet', context, layer, name),
                    callable=zcml.handler,
                    args=('registerAdapter', new_class,
                          (context, layer),
                          IPagelet, name, _context.info))

    # Register view
    config = with_context(_context)
    config.add_view(name=name,
                    view=new_class,
                    context=context,
                    permission=permission,
                    request_type=layer)


def _handle_for(_context, for_):
    if for_ is not None:
        _context.action(discriminator=None,
                        callable=provideInterface,
                        args=('', for_))
