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
import os
import unittest, doctest
from zope import interface, component
from zope.app.testing import setup
from zope.app.rotterdam import Rotterdam
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.component.hooks import setSite
from zope.app.security import principalregistry
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.testing.functional import getRootFolder, sync
from zope.app.testing.functional import ZCMLLayer, Functional, FunctionalTestSetup
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.catalog.catalog import Catalog, ICatalog


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """

class IDefaultPermissionCategory(interface.Interface):
    """ """


def FunctionalDocFileSuite(*paths, **kw):
    globs = kw.setdefault('globs', {})
    globs['sync'] = sync
    globs['getRootFolder'] = getRootFolder

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        FunctionalTestSetup().setUp()

        root = getRootFolder()
        setSite(root)

        root['ids'] = IntIds()
        root.getSiteManager().registerUtility(root['ids'], IIntIds)

        root['catalog'] = Catalog()
        root.getSiteManager().registerUtility(root['catalog'], ICatalog)


    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        old = doctest.set_unittest_reportflags(0)
        doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (old
                             | doctest.ELLIPSIS
                             | doctest.NORMALIZE_WHITESPACE)

    layer = kw.get('layer', Functional)
    if 'layer' in kw:
        del kw['layer']

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite

def setUp(tests):
    setup.placelessSetUp(tests)

    anon = principalregistry.UnauthenticatedPrincipal(
        'zope.anonymous', 'Anonymous', '')
    component.provideUtility(anon, IUnauthenticatedPrincipal)


principalRoles = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'principalRoles', allow_teardown=True)


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite(
                'zojax.principal.roles.defaultroles',
                setUp=setUp, tearDown=setup.placelessTearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            FunctionalDocFileSuite('preferences.txt', layer=principalRoles),
            FunctionalDocFileSuite('configlet.txt', layer=principalRoles),
            ))
