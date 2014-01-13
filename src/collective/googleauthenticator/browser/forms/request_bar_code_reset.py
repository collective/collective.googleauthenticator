"""
Request the bar code reset.
"""
import logging
from smtplib import SMTPRecipientsRefused

from zope.i18nmessageid import MessageFactory
from zope.schema import TextLine
from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from ska import Signature, RequestHelper

from collective.googleauthenticator.helpers import get_ska_secret_key

logger = logging.getLogger('collective.googleauthenticator')

_ = MessageFactory('collective.googleauthenticator')


class IRequestBarCodeResetForm(form.Schema):
    """
    Interface for the request to reset the Google Authenticator bar code form.
    """
    username = TextLine(
        title=_(u'Username'),
        description=_(u'Enter your username for verification. The link code to reset the '
                      u'bar code would be sent to your email.'),
        required=True
    )


class RequestBarCodeResetForm(form.SchemaForm):
    """
    Form for request to reset to the Google Authenticator bar code form.
    """
    fields = field.Fields(IRequestBarCodeResetForm)
    ignoreContext = True
    schema = IRequestBarCodeResetForm
    label = _("Request to reset the Google Authenticator bar code")
    description = _(u"Enter your username for verification. The link code to reset the "
                    u"bar code would be sent to your email.")

    @button.buttonAndHandler(_('Submit'))
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        username = data.get('username', '')

        user = api.user.get(username=username)

        reason = None
        if user:
            try:
                # Here we need to generate a token which is valid for let's say, 2 hours
                # using which it should be possible to reset the bar-code. The `signature`
                # generated should be saved in the user profile `bar_code_reset_token`.
                ska_secret_key = get_ska_secret_key(request=self.request, user=user)
                signature = Signature.generate_signature(
                    auth_user = username,
                    secret_key = ska_secret_key,
                    lifetime = 7200 # 2 hours
                    )
                request_helper = RequestHelper(
                    signature_param = 'signature',
                    auth_user_param = 'auth_user',
                    valid_until_param = 'valid_until'
                    )

                signed_url = request_helper.signature_to_url(
                    signature = signature,
                    endpoint_url = '{0}/{1}'.format(self.context.absolute_url(), '@@reset-bar-code')
                )

                # Save the `signature` value to the `bar_code_reset_token`.
                user.setMemberProperties(mapping={'bar_code_reset_token': str(signature),})

                # Now we need to send an email to user with URL in and a small explanations.
                try:
                    host = getToolByName(self, 'MailHost')

                    mail_text_template = self.context.restrictedTraverse('request_bar_code_reset_email')
                    mail_text = mail_text_template(
                        member = user,
                        bar_code_reset_url = signed_url,
                        charset = 'utf-8'
                        )

                    host.send(
                        mail_text,
                        immediate = True
                        )
                except SMTPRecipientsRefused as e:
                    raise SMTPRecipientsRefused('Recipient address rejected by server')

                IStatusMessage(self.request).addStatusMessage(
                    _("An email with instructions on resetting your bar-code is sent successfully."),
                    'info'
                    )
                redirect_url = "{0}".format(self.context.absolute_url())
                self.request.response.redirect(redirect_url)
            except ValueError as e:
                reason = _(str(e))
        else:
            reason = _("Invalid username.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(
                _("Request for bar-code reset is failed! {0}".format(reason)),
                'error'
                )

    def updateFields(self, *args, **kwargs):
        """
        """
        return super(RequestBarCodeResetForm, self).updateFields(*args, **kwargs)


# View for the ``RequestBarCodeResetForm``.
RequestBarCodeResetFormView = wrap_form(RequestBarCodeResetForm)
