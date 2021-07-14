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

"""PyAMS_portal.portlets.jumbotron.interfaces module


"""

from zope.interface import Invalid, invariant
from zope.schema import Bool, Choice, URI

from pyams_i18n.schema import I18nTextField, I18nTextLineField
from pyams_portal.interfaces import IPortletSettings
from pyams_sequence.schema import InternalReferenceField
from pyams_skin.interfaces import BOOTSTRAP_STATUS


__docformat__ = 'restructuredtext'

from pyams_portal import _  # pylint: disable=ungrouped-imports


class IJumbotronPortletSettings(IPortletSettings):
    """Jumbotron portlet settings interface"""

    title = I18nTextLineField(title=_("Title"),
                              description=_("Main component title"),
                              required=True)

    lead = I18nTextLineField(title=_("Leading text"),
                             description=_("Short text to be displayed below title"),
                             required=False)

    display_ruler = Bool(title=_("Display ruler"),
                         description=_("If 'yes', an horizontal line will be displayed "
                                       "between leading text and body"),
                         required=True,
                         default=True)

    body = I18nTextField(title=_("Body"),
                         description=_("Main text"),
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
