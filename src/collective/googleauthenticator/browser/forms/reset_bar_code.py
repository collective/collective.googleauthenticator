"""
Reset bar-code.
"""
import logging

from zope.i18nmessageid import MessageFactory

from z3c.form import button, field

from plone.directives import form
from plone import api
from plone.z3cform.layout import wrap_form

from Products.statusmessages.interfaces import IStatusMessage
from zope.schema import TextLine

from collective.googleauthenticator.helpers import get_token_description, validate_token, validate_user_data

logger = logging.getLogger('collective.googleauthenticator')

_ = MessageFactory('collective.googleauthenticator')


class IResetBarCodeForm(form.Schema):
    """
    Interface for the Google Authenticator Reset Bar Code form.
    """

    # The qr_code field isn't used as a input field, instead it is used to show the QR code
    qr_code = TextLine(
        title=_(u'1. Scan this QR code with the Google Authenticator app'),
        description=u'This description is replaced with the QR code.',
        required=False
    )
    token = TextLine(
        title=_(u'2. Enter the verification code to activate two-step verification '),
        description=_(u'The Google Authenticator app generates a verification code, '
                      u'enter the code below'),
        required=True
    )


class ResetBarCodeForm(form.SchemaForm):
    """
    Form for the Google Authenticator Reset Bar Code.

    What happens here is:

    - Signed user data is validated. If valid, the user is fetched.
    - Token (`signature` param) is matched to the one obtained from user records. If matched, the
      bar-code image is reset (security token is reset and saved in the users' profile).
    """
    fields = field.Fields(IResetBarCodeForm)
    ignoreContext = True
    schema = IResetBarCodeForm
    label = _("Reset your two-step verification bar-code")
    description = _(u"To reset the two-step verification bar-code you need to install the Google"
                    u"Authenticator app on your phone. This app is available for "
                    u"Android, iOS and BlackBerry devices.")

    def action(self):
        return "{0}?{1}".format(
            self.request.getURL(),
            self.request.get('QUERY_STRING', '')
            )

    @button.buttonAndHandler(_('Verify'))
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        # Token entered by user from his mobile device using GoogleAuthenticator app
        token = data.get('token', '')

        # Signature token generated for resetting the bar code.
        signature_token = self.request.get('signature', '')

        username = self.request.get('auth_user', '')
        user = api.user.get(username=username)

        #logger.debug('token: {0}'.format(token))

        if not user:
            reason = _("User not found {0}.".format(username))
            IStatusMessage(self.request).addStatusMessage(
                _("Resetting of the bar-code failed! {0}".format(reason)),
                'error'
                )
            return

        # Validating the GoogleAuthenticator app token
        valid_token = validate_token(token, user=user)

        #self.context.plone_log(valid_token)
        #self.context.plone_log(token)

        reason = None
        if valid_token:
            try:
                # Checking if token generated for resetting the bar code image is equal
                # to the one taken from current request.
                bar_code_reset_token = user.getProperty('bar_code_reset_token')
                if bar_code_reset_token != signature_token:
                    reason = _("Invalid bar-code reset token.")
                    IStatusMessage(self.request).addStatusMessage(
                        _("Resetting of the bar-code failed! {0}".format(reason)),
                        'error'
                        )
                    return

                user.setMemberProperties(mapping={'enable_two_factor_authentication': True,})

                IStatusMessage(self.request).addStatusMessage(
                    _("Two-step verification bar-code is successfully reset for your account."),
                    'info'
                    )
                redirect_url = "{0}".format(self.context.absolute_url())
                self.request.response.redirect(redirect_url)
            except Exception as e:
                reason = _(str(e))
        else:
            reason = _("Invalid token or token expired.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(_("Setup failed! {0}".format(reason)), 'error')

    def updateFields(self, *args, **kwargs):
        """
        Here happens the following:

        - Signed user data is validated. If valid, the user is fetched.
        - Token (`signature` param) is matched to the one obtained from user records. If matched, the
          bar-code image is reset (security token is reset and saved in the users' profile).
        """
        # Adding a proper description (with bar code image)
        barcode_field = self.fields.get('qr_code')

        username = self.request.get('auth_user', '')
        token = self.request.get('signature', '')
        user = api.user.get(username=username)

        # If valid user
        if user:
            # Getting the users' bar-code reset token saved in his profile.
            bar_code_reset_token = user.getProperty('bar_code_reset_token')

            # Validate the user data
            user_data_validation_result = validate_user_data(request=self.request, user=user)

            # If all goes well, regenerate the token (overwrite_secret=True) and show the bar code image.
            if barcode_field:
                if user_data_validation_result.result and bar_code_reset_token == token:
                    barcode_field.field.description = _(get_token_description(user=user, overwrite_secret=False))
                else:
                    if not user_data_validation_result.result:
                        IStatusMessage(self.request).addStatusMessage(
                            ' '.join(user_data_validation_result.reason),
                            'error'
                            )
                    else:
                        IStatusMessage(self.request).addStatusMessage(
                            _("Invalid bar-code reset token"),
                            'error'
                            )

        return super(ResetBarCodeForm, self).updateFields(*args, **kwargs)


# View for the ``ResetBarCodeForm``.
ResetBarCodeFormView = wrap_form(ResetBarCodeForm)
