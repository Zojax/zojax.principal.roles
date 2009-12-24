##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import interface, event
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent
from zope.securitypolicy.interfaces import Allow, Deny, Unset

from zojax.statusmessage.interfaces import IStatusMessage
from zojax.principal.roles.interfaces import _, IPublicRole


class EditRolesForm(object):

    _settings = {Allow: 1, Deny:2, Unset:3}

    def update(self):
        context = self.context
        request = self.request

        if 'form.save' in request:
            roles = {}
            for role, setting in request.form.items():
                if setting == '1':
                    roles[role] = Allow
                elif setting == '2':
                    roles[role] = Deny
                else:
                    roles[role] = Unset

            context.roles = roles
            event.notify(ObjectModifiedEvent(context))
            IStatusMessage(request).add(_('Roles have been changed.'))

        roles = []
        for rid, setting in self.context.roles.items():
            role = getUtility(IPublicRole, rid)

            roles.append((
                    role.title, rid,
                    {'id': rid,
                     'title': role.title,
                     'setting': self._settings[setting]}))

        roles.sort()
        self.roles = [info for t,i,info in roles]
