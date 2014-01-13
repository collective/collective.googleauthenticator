from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import TextLine

from plone.app.registry.browser import controlpanel

_ = MessageFactory('collective.googleauthenticator')


class IGoogleAuthenticatorSettings(Interface):
    """
    Global Google Authenticator settings.
    """
    ska_secret_key = TextLine(
        title = _("Secret Key"),
        description = _("Enter your secret key for the site here. When choosing a secret key, "
                        "think of it as some sort of a password."),
        required = False,
        default = u'',
        )


class GoogleAuthenticatorSettingsEditForm(controlpanel.RegistryEditForm):
    """
    Control panel form.
    """
    schema = IGoogleAuthenticatorSettings
    label = _("Google Authenticator settings")
    description = _(u"""""")

    def updateFields(self):
        super(GoogleAuthenticatorSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(GoogleAuthenticatorSettingsEditForm, self).updateWidgets()


class GoogleAuthenticatorSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    Control panel.
    """
    form = GoogleAuthenticatorSettingsEditForm
