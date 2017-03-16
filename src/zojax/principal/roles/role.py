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
from rwproperty import setproperty, getproperty

from zope import interface, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.app.component.hooks import getSite
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.app.intid.interfaces import IIntIds, IIntIdAddedEvent, IIntIdRemovedEvent
from zojax.content.type.item import PersistentItem

from interfaces import IPortalRole


class PortalRole(PersistentItem):
    interface.implements(IPortalRole)

    @setproperty
    def id(self, value):
        pass

    @getproperty
    def id(self):
        try:
            return u'role%s' % getUtility(IIntIds).getId(self)
        except KeyError:
            pass


@component.adapter(IPortalRole, IIntIdAddedEvent)
def portalRoleAdded(role, ev):
    sm = component.getSiteManager()
    sm.registerUtility(role, IPortalRole, role.id)


@component.adapter(IPortalRole, IIntIdRemovedEvent)
def portalRoleRemoved(role, ev):
    rid = role.id
    sm = component.getSiteManager()
    sm.unregisterUtility(role, IPortalRole, rid)

    roleperm = removeAllProxies(IRolePermissionManager(getSite()))

    for permId, setting in list(roleperm.getPermissionsForRole(rid)):
        roleperm.unsetPermissionFromRole(permId, rid)
