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
from rwproperty import getproperty, setproperty

from zope import interface, component
from zope.component import getUtilitiesFor
from zope.security.management import queryInteraction
from zope.app.component.hooks import getSite
from zope.app.security.settings import Allow, Deny, Unset
from zope.securitypolicy.interfaces import IRole, IPrincipalRoleManager

from interfaces import IPublicRole


class RolesPreference(object):

    def __bind__(self, principal=None, parent=None):
        clone = super(RolesPreference, self).__bind__(principal, parent)
        clone._roles = [name for name, role in getUtilitiesFor(IPublicRole)]
        return clone

    @getproperty
    def roles(self):
        principal_id = self.__principal__.id
        rolemanager = IPrincipalRoleManager(getSite())

        roles = {}
        for rid in self._roles:
            roles[rid] = Unset

        for role, setting in rolemanager.getRolesForPrincipal(principal_id):
            if role in self._roles:
                roles[role] = setting

        return roles

    @setproperty
    def roles(self, value):
        principal_id = self.__principal__.id
        rolemanager = IPrincipalRoleManager(getSite())

        for role, setting in value.items():
            if role not in self._roles:
                continue

            if setting is Allow:
                rolemanager.assignRoleToPrincipal(role, principal_id)
            elif setting is Deny:
                rolemanager.removeRoleFromPrincipal(role, principal_id)
            else:
                rolemanager.unsetRoleForPrincipal(role, principal_id)

    def isAvailable(self):
        if not super(RolesPreference, self).isAvailable():
            return False

        interaction = queryInteraction()
        if interaction is not None:
            principal_id = None
            for participation in interaction.participations:
                principal_id = participation.principal.id
                break

            return principal_id != self.__principal__.id

        return False
