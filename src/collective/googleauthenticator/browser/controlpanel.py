# coding=utf-8
from plone import api
from plone.app.registry.browser import controlpanel
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform.form import AutoExtensibleForm
from plone.directives.form import fieldset
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from zope.component import getUtility
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
        description = _("If checked, globally enables the two-step verification for all users; "
                        "otherwise - each user configures it himself. Note, that unchecking the "
                        "checkbox does not disable the two-step verification for all users."),
        required = False,
        default = True,
        )
    ip_addresses_whitelist = Text(
        title = _("White-listed IP addresses"),
        description = _("Two-step verification will be ommit for users that log in from white "
                        "listed addresses."),
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
    additional_template = ViewPageTemplateFile("templates/control_panel_extra.pt")

    def render(self, *args, **kwargs):
        res = super(GoogleAuthenticatorSettingsEditForm, self).render(*args, **kwargs)
        additional = self.additional_template(
            enable_url = '{0}/{1}'.format(self.context.absolute_url(), '@@google-authenticator-enable-for-all-users'),
            enable_text = _("Enable two-step verification for all users"),
            disable_url = '{0}/{1}'.format(self.context.absolute_url(), '@@google-authenticator-disable-for-all-users'),
            disable_text = _("Disable two-step verification for all users"),
            charset = 'utf-8',
            )
        return res + additional

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        """
        Update properties of all users.
        """
        from collective.googleauthenticator.helpers import (
            enable_two_factor_authentication_for_users, disable_two_factor_authentication_for_users
            )
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        globally_enabled = data.get('globally_enabled', None)

        if globally_enabled is True:
            # Enable for all users
            users = api.user.get_users()
            enable_two_factor_authentication_for_users(users)
            logger.debug('Enabled')
        elif globally_enabled is False:
            # Disable for all users
            users = api.user.get_users()
            #disable_two_factor_authentication_for_users(users)
            logger.debug('Disabled')

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
