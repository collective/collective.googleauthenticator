from uuid import uuid4

from zope.i18nmessageid import MessageFactory

from collective.googleauthenticator.helpers import get_app_settings
from collective.googleauthenticator.pas_plugin import GoogleAuthenticatorPlugin

_ = MessageFactory('collective.googleauthenticator')

PAS_TITLE = 'Google Authenticator plugin (collective.googleauthenticator)'
PAS_ID = 'google_auth'

def _add_plugin(pas, pluginid=PAS_ID):
    """
    Install and activate collective.googleauthenticator PAS plugin
    """
    installed = pas.objectIds()
    if pluginid in installed:
        return PAS_TITLE + " already installed."
    plugin = GoogleAuthenticatorPlugin(pluginid, title=PAS_TITLE)
    pas._setObject(pluginid, plugin)
    plugin = pas[plugin.getId()] # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info['interface']
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        pas.plugins.movePluginsDown(
            interface,
            [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
        )

def _setup_secret_key(portal):
    """
    Generate secret key
    """
    portal.portal_setup.runImportStepFromProfile(
        'profile-collective.googleauthenticator:default',
        'plone.app.registry'
        )

    settings = get_app_settings()
    if not settings.ska_secret_key:
        settings.ska_secret_key = unicode(uuid4())

def setupVarious(context):
    """
    @param context: Products.GenericSetup.context.DirectoryImportContext instance
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('collective.googleauthenticator.marker.txt') is None:
        # Not your add-on
        return

    portal = context.getSite()

    _setup_secret_key(portal)

    pas = portal.acl_users
    _add_plugin(pas)


