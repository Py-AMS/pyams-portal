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

"""PyAMS_pagelet.interfaces module

"""

from pyramid.interfaces import IView
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Attribute, implementer
from zope.interface.interfaces import IObjectEvent, ObjectEvent


__docformat__ = 'restructuredtext'


class IPagelet(IView):
    """Pagelet interface"""

    def update(self):
        """Update the pagelet data."""

    def render(self):
        """Render the pagelet content w/o o-wrap."""


class IPageletRenderer(IContentProvider):
    """Render a pagelet by calling it's 'render' method"""


class IPageletCreatedEvent(IObjectEvent):
    """Pagelet created event interface"""

    request = Attribute('The request object')


@implementer(IPageletCreatedEvent)
class PageletCreatedEvent(ObjectEvent):
    """Pagelet created event"""

    def __init__(self, object):  # pylint: disable=redefined-builtin
        super(PageletCreatedEvent, self).__init__(object)
        self.request = object.request
