# coding=utf-8
from collective.googleauthenticator.testing import COLLECTIVE_GOOGLEAUTHENTICATOR_INTEGRATION_TESTING  # noqa: E501
from collective.googleauthenticator.tests.base import BaseTest
from plone import api
from plone.app.testing import quickInstallProduct
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName

import unittest


class TestGeneric(unittest.TestCase, BaseTest):

    layer = COLLECTIVE_GOOGLEAUTHENTICATOR_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        self.portal_url = api.portal.get().absolute_url()

    def test_(self):
        """
        """
