# coding=utf-8
from plone import api
from plone.app.registry.browser import controlpanel
from plone.app.registry.browser.controlpanel import RegistryEditForm
from z3c.form import button
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Text
from zope.schema import TextLine

import logging


logger = logging.getLogger("collective.googleauthenticator")

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
    globally_enabled = Bool(
        title = _("Globally enabled"),
        description = _(
            "If checked, two-step verification will be required for all users. "
            "If unchecked, two-step verification will be skipped for all users."),
        required = False,
        default = True,
        )
    ip_addresses_whitelist = Text(
        title = _("IP address allowlist"),
        description = _("Two-step verification will be skipped for users that log in from "
                        "addresses in the allowlist."),
        required = False,
        default = u'',
        )


class GoogleAuthenticatorSettingsEditForm(RegistryEditForm):
    """
    Control panel form.
    """
    control_panel_view = "plone_control_panel"
    schema_prefix = None
    schema = IGoogleAuthenticatorSettings
    label = _("Google Authenticator")
    description = _(u"""Google Authenticator configuration""")
    enable_unload_protection = False

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        """
        Update properties of all users.
        """
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        changes = self.applyChanges(data)
        api.portal.show_message(_(u"Changes saved."), self.request, "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(_(u"Edit cancelled."), self.request, "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))


class GoogleAuthenticatorSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    Control panel.
    """
    form = GoogleAuthenticatorSettingsEditForm
