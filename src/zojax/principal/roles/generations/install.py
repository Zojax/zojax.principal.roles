##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
import sys, types
from zope import interface, event
from zope.proxy import removeAllProxies, sameProxiedObjects
from zope.securitypolicy.interfaces import Allow, Unset
from zope.securitypolicy.interfaces import IRole, IRolePermissionManager
from zope.app.component.interfaces import ISite
from zope.app.publication.zopepublication import ZopePublication
from zope.app.generations.utility import findObjectsProviding
from zojax.principal.roles.role import PortalRole
from zojax.principal.roles.interfaces import IPortalRole, IPublicRole

class IOldPublicRole(interface.Interface):
    pass


modId = 'zojax.roles.interfaces'
if  'zojax.roles' not in sys.modules:
    sys.modules['zojax.roles'] = types.ModuleType('zojax.roles')
    sys.modules[modId] = types.ModuleType(modId)
    sys.modules[modId].IPublicRole = IOldPublicRole


def evolve(context):
    root = context.connection.root()[ZopePublication.root_name]

    for site in findObjectsProviding(root, ISite):
        sm = site.getSiteManager()
        roleperm = IRolePermissionManager(site)

        for name, role in sm.getUtilitiesFor(IRole):
            if isinstance(role, PortalRole):
                sm.unregisterUtility(role, IRole, name)
                sm.unregisterUtility(role, IPublicRole, name)
                sm.unregisterUtility(role, IPortalRole, name)
                sm.unregisterUtility(role, IOldPublicRole, name)

                sm.registerUtility(role, IPortalRole, name)

                if hasattr(role, 'permissions'):
                    for permId, setting in role.permissions.items():
                        if sameProxiedObjects(setting, Allow):
                            roleperm.grantPermissionToRole(permId, name)
                        else:
                            roleperm.unsetPermissionFromRole(permId, name)

                    del role.permissions
