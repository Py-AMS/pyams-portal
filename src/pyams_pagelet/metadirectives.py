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

"""PyAMS_paget.metadirectives module

This module provides interface of ZCML directives.
"""

from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import TextLine


__docformat__ = 'restructuredtext'


class IPageletDirective(Interface):
    """Pagelet ZCML directive interface"""

    name = TextLine(title='The name of the view',
                    description='Shows up in URLs/paths. For example "foo" or "foo.html"',
                    required=True)

    context = GlobalObject(title='The interface or class this view is for',
                           required=False)

    layer = GlobalObject(title="The request interface or class this pagelet is for",
                         description="Defaults to pyramid.interfaces.IRequest",
                         required=False)

    view = GlobalObject(title='View class',
                        description='The view function or class',
                        required=True)

    permission = TextLine(title='Permission',
                          description='The permission needed to use the view',
                          required=False)


# pylint: disable=no-value-for-parameter
IPageletDirective.setTaggedValue('keyword_arguments', True)
