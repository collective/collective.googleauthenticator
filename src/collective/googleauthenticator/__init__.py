# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory

from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin

from collective.googleauthenticator.pas_plugin import (
    GoogleAuthenticatorPlugin, addGoogleAuthenticatorPlugin, manage_addGoogleAuthenticatorPluginForm
    )

_ = MessageFactory('collective.googleauthenticator')

def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
    registerMultiPlugin(GoogleAuthenticatorPlugin.meta_type) # Add to PAS menu
    context.registerClass(
        GoogleAuthenticatorPlugin,
        constructors = (manage_addGoogleAuthenticatorPluginForm, addGoogleAuthenticatorPlugin),
        visibility = None
        )
