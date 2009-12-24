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
from zope import interface
from zope.proxy import sameProxiedObjects, removeAllProxies
from zope.component import getUtilitiesFor
from zope.app.component.hooks import getSite
from zope.security.interfaces import IPermission
from zope.securitypolicy.interfaces import Allow, Unset, IRolePermissionManager

from zojax.wizard.step import WizardStep
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.security.interfaces import \
    IPublicRole, IManagerRole, IPublicPermission, IPermissionCategoryType

from zojax.principal.roles.interfaces import _


class PortalRoles(WizardStep):

    def update(self):
        super(PortalRoles, self).update()

        roleperm = removeAllProxies(IRolePermissionManager(getSite()))

        # roles
        roles = []
        for name, role in getUtilitiesFor(IPublicRole):
            if IManagerRole.providedBy(role):
                continue

            roles.append((role.title,
                          {'id': name,
                           'title': role.title,
                           'name': name.replace('.', '_')}))

        roles.sort()
        roles = [info for _t, info in roles]
        self.roles = roles

        # permissions
        permissions = []
        for name, perm in getUtilitiesFor(IPermission):
            if not IPublicPermission.providedBy(perm):
                continue

            permissions.append(
                {'name': name, 'permission': perm, 'settings': {},
                 'title': perm.title, 'desc': perm.description})

        # process form
        request = self.request
        if 'form.updatePermissions' in request:

            for role in roles:
                roleId = role['id']
                settings = request.get(u'role-%s'%roleId, ())

                for perm in permissions:
                    permId = perm['name']
                    if permId in settings:
                        roleperm.grantPermissionToRole(permId, roleId)
                    else:
                        roleperm.unsetPermissionFromRole(permId, roleId)

            IStatusMessage(request).add(
                _('Roles permissions have been updated.'))

        # categories
        categories = []
        for name, category in getUtilitiesFor(IPermissionCategoryType):
            categories.append([name, category.__doc__, category, []])

        for perm in permissions:
            for info in categories:
                if info[2].providedBy(perm['permission']):
                    for role in self.roles:
                        perm['settings'][role['id']] = sameProxiedObjects(
                            roleperm.getSetting(perm['name'], role['id']), Allow)

                    info[3].append((perm['title'], perm))

        for info in categories:
            info[3].sort()
            info[3] = [p for _t, p in info[3]]

        categories.sort()
        self.permissions = [
            {'name': name, 'desc':desc, 'perms': perms}
            for name, desc, cat, perms in categories if perms]

    def isAvailable(self):
        if not self.roles or not self.permissions:
            return False

        return super(PortalRoles, self).isAvailable()
