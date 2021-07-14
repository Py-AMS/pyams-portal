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

"""PyAMS_portal.portlets.cards.interfaces module

"""

from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.interface import Invalid, invariant
from zope.location.interfaces import IContained
from zope.schema import Bool, Choice, TextLine, URI

from pyams_file.schema import ImageField
from pyams_i18n.schema import I18nTextField, I18nTextLineField
from pyams_portal.interfaces import IPortletSettings
from pyams_sequence.schema import InternalReferenceField
from pyams_skin.interfaces import BOOTSTRAP_STATUS


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class ICard(IContained):
    """Bootstrap card interface"""

    visible = Bool(title=_("Visible card?"),
                   required=True,
                   default=True)

    title = I18nTextLineField(title=_("Card's title"),
                              required=False)

    illustration = ImageField(title=_("Illustration"),
                              description=_("Card's illustration"),
                              required=False)

    body = I18nTextField(title=_("Body"),
                         description=_("Main card's text"),
                         required=False)

    reference = InternalReferenceField(title=_("Button internal target"),
                                       description=_("Optional button reference target"),
                                       required=False)

    target_url = URI(title=_("Button external URI"),
                     description=_("Alternate URI target used for optional button"),
                     required=False)

    @invariant
    def check_target(self):
        """Check for internal reference or external URL"""
        if self.reference and self.target_url:
            raise Invalid(_("You can only set an internal target OR an external URL..."))

    button_label = I18nTextLineField(title=_("Button label"),
                                     description=_("Optional button label"),
                                     required=False)

    button_status = Choice(title=_("Button status"),
                           description=_("Status of optional button"),
                           values=BOOTSTRAP_STATUS,
                           default='primary')

    css_class = TextLine(title=_("CSS class"),
                         description=_("Card's CSS class"),
                         default='col mb-3')


class ICardsPortletSettings(IPortletSettings, IContainer):
    """Bootstrap cards portlet settings interface"""

    contains(ICard)

    title = I18nTextLineField(title=_("Title"),
                              description=_("Main component title"),
                              required=False)

    lead = I18nTextLineField(title=_("Leading text"),
                             description=_("Short text to be displayed below title"),
                             required=False)

    def get_visible_items(self):
        """Get iterator over visible cards"""
