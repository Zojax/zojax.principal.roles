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
from zope import interface, component
from zope.component import getUtility, queryUtility
from zope.app.component.interfaces import ISite
from zope.app.security.settings import Allow, Unset
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IEveryoneGroup
from zope.app.security.interfaces import IUnauthenticatedGroup
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.securitypolicy.interfaces import IPrincipalRoleMap

from interfaces import IDefaultPortalRole


class DefaultPrincipalRoleMap(object):
    """
    >>> sm = component.getSiteManager()
    >>> from zope.app.security.interfaces import IAuthentication
    >>> class Auth(object):
    ...     prefix = 'xyz'
    >>> auth = Auth()

    >>> sm.registerUtility(auth, IAuthentication)

    >>> class DefaultPortalRole(object):
    ...     interface.implements(IDefaultPortalRole)
    ...     roles = ('portal.Member',)
    >>> component.provideUtility(DefaultPortalRole(), IDefaultPortalRole)

    >>> map = DefaultPrincipalRoleMap(None)
    >>> map.getPrincipalsForRole('portal.Member')
    ()
    >>> map.getRolesForPrincipal('xyz_user')
    [('portal.Member', PermissionSetting: Allow)]

    >>> map.getSetting('portal.Member', 'xyz_user')
    PermissionSetting: Allow
    >>> map.getSetting('portal.Manager', 'xyz_user')
    PermissionSetting: Unset

    >>> map.getRolesForPrincipal('zope.Anonymous')
    ()

    >>> map.getPrincipalsAndRoles()

    >>> data = sm.unregisterUtility(auth, IAuthentication)

    """
    component.adapts(ISite)
    interface.implements(IPrincipalRoleMap)

    def __init__(self, context):
        auth = getUtility(IAuthentication)
        self.prefix = getattr(auth, 'prefix', '---------------')
        self.roles = getUtility(IDefaultPortalRole).roles
        self.anon = (getUtility(IUnauthenticatedPrincipal).id,)

        grp = queryUtility(IUnauthenticatedGroup)
        if grp is not None:
            self.anon = self.anon + (grp.id, )

        grp = queryUtility(IEveryoneGroup)
        if grp is not None:
            self.anon = self.anon + (grp.id, )

    def getPrincipalsForRole(self, role_id):
        return ()

    def getRolesForPrincipal(self, principal_id):
        if principal_id not in self.anon and \
                principal_id.startswith(self.prefix) and self.roles:
            return [(role, Allow) for role in self.roles]
        return ()

    def getSetting(self, role_id, principal_id):
        if principal_id not in self.anon and \
                principal_id.startswith(self.prefix) and (role_id in self.roles):
            return Allow
        return Unset

    def getPrincipalsAndRoles(self):
        pass
