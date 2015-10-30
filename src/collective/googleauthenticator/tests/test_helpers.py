import unittest2 as unittest

from collective.googleauthenticator.testing import \
    COLLECTIVE_GOOGLEAUTHENTICATOR_INTEGRATION_TESTING
from collective.googleauthenticator.tests.base import BaseTest

from collective.googleauthenticator.helpers import get_ip_ranges
from ipaddress import IPv4Network
from ipaddress import IPv4Address


class TestIPWhitelisting(unittest.TestCase, BaseTest):

    layer = COLLECTIVE_GOOGLEAUTHENTICATOR_INTEGRATION_TESTING

    def test_get_ip_ranges_always_returns_networks_and_accepts_single_ip(self):
        ranges = get_ip_ranges(['127.0.0.1', '192.168.0.0/16'])
        self.assertEqual(
            [IPv4Network('127.0.0.1'), IPv4Network('192.168.0.0/16')],
            ranges)

    def test_get_ip_ranges_can_be_used_for_containment_testing(self):
        ranges = get_ip_ranges(['127.0.0.1', '192.168.0.0/16'])
        self.assertTrue(any(IPv4Address('127.0.0.1') in r for r in ranges))
        self.assertTrue(any(IPv4Address('192.168.1.1') in r for r in ranges))
        self.assertFalse(any(IPv4Address('10.0.0.0') in r for r in ranges))
