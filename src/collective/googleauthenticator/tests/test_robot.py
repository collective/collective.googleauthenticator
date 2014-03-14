from  collective.googleauthenticator.testing import COLLECTIVE_GOOGLEAUTHENTICATOR_ROBOT_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_test.txt"),
                layer=COLLECTIVE_GOOGLEAUTHENTICATOR_ROBOT_TESTING)
    ])
    return suite