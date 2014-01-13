from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivegoogleauthenticatorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.googleauthenticator
        xmlconfig.file(
            'configure.zcml',
            collective.googleauthenticator,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'collective.googleauthenticator')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'collective.googleauthenticator')


COLLECTIVE_GOOGLEAUTHENTICATOR_FIXTURE = CollectivegoogleauthenticatorLayer()
COLLECTIVE_GOOGLEAUTHENTICATOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_GOOGLEAUTHENTICATOR_FIXTURE,),
    name="CollectivegoogleauthenticatorLayer:Integration"
)
COLLECTIVE_GOOGLEAUTHENTICATOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_GOOGLEAUTHENTICATOR_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivegoogleauthenticatorLayer:Functional"
)
