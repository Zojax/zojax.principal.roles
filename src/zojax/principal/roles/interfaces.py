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
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zope.securitypolicy.interfaces import IRole
from zojax.security.interfaces import IPublicRole
from zojax.widget.checkbox.field import CheckboxList

_ = MessageFactory('zojax.principal.roles')


class IPortalRole(IRole, IPublicRole):
    """ portal role """

    id = interface.Attribute('Permissions')


class IPortalRoles(interface.Interface):
    """ portal roles configlet """


class IDefaultPortalRole(interface.Interface):
    """ default portal role configlet """

    roles = CheckboxList(
        title = _(u'Default roles'),
        description = _(u'Select default roles for portal principals.'),
        vocabulary = "zojax.roles",
        required = False,
        default = [],
        missing_value = [])


class IRolesPreference(interface.Interface):
    """ principal roles """

    roles = schema.TextLine(
        title = _(u'Roles'))
