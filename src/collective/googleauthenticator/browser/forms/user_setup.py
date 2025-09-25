"""
User setup.
"""

import logging

from zope.i18nmessageid import MessageFactory

from z3c.form import button, field

from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from plone import api

from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.form import Form
from zope.schema import TextLine

from collective.googleauthenticator.helpers import get_qr_code, validate_token
from collective.googleauthenticator.helpers import disable_csrf_check
from collective.googleauthenticator.helpers import drop_login_failed_msg
from collective.googleauthenticator.helpers import validate_user_data
from collective.googleauthenticator.helpers import extract_request_data
from collective.googleauthenticator.helpers import login_user

logger = logging.getLogger("collective.googleauthenticator")

_ = MessageFactory("collective.googleauthenticator")
PMF = MessageFactory("plone")


class ISetupForm(model.Schema):
    """
    Interface for the Google Authenticator setup form.
    """

    token = TextLine(
        title=_("2. Enter the verification code to activate two-step verification "),
        description=_(
            "The Google Authenticator app generates a verification code, "
            "enter the code below"
        ),
        required=True,
    )


class SetupForm(AutoExtensibleForm, Form):
    """
    Form for the Google Authenticator setup.
    """

    fields = field.Fields(ISetupForm)
    ignoreContext = True
    schema = ISetupForm
    label = _("Setup two-step verification")
    description = _(
        "help_2fa_setup",
        default="To proceed with this two-step verification, "
        "the Google Authenticator app must be installed on your phone. "
        "Open your phone's photo app and point the camera at the QR code. "
        "Do NOT take a photo, but click the link that appears. "
        "This will open Google Authenticator which will then generate a code.",
    )

    @property
    def user(self):
        # If already authenticated, use current user
        user = api.user.get_current()
        if user.getUserName() != "Anonymous User":
            return user

        # Otherwise get user from signed request data.
        username = self.request.get("auth_user", "")
        if username:
            user = api.user.get(username=username)

            # Validating the signed request data. If invalid (likely tampered
            # with or expired), generate an appropriate error message.
            user_data_validation_result = validate_user_data(
                request=self.request, user=user
            )
            if not user_data_validation_result.result:
                IStatusMessage(self.request).addStatusMessage(
                    _(
                        "Invalid data. Details: {0}".format(
                            " ".join(user_data_validation_result.reason)
                        )
                    ),
                    "error",
                )
                return
            return user

    def action(self):
        return "{0}?{1}".format(
            self.request.getURL(), self.request.get("QUERY_STRING", "")
        )

    @button.buttonAndHandler(_("Verify"))
    def handleSubmit(self, action):
        user = self.user
        if user is None:
            self.request.response.setStatus(401, _("Forbidden for anonymous"), True)
            return False

        data, errors = self.extractData()
        if errors:
            return False

        token = data.get("token", "")

        valid_token = validate_token(token, user=user)

        reason = None
        if valid_token:
            try:
                # Set the ``enable_two_factor_authentication`` to True
                user.setMemberProperties(
                    mapping={
                        "enable_two_factor_authentication": True,
                    }
                )
                IStatusMessage(self.request).addStatusMessage(
                    _(
                        "Two-step verification is successfully enabled for your account."
                    ),
                    "info",
                )
                if api.user.get_current().getUserName() != "Anonymous User":
                    redirect_url = "{0}/@@personal-information".format(
                        self.context.absolute_url()
                    )
                else:
                    login_user(user.getUser())
                    msg = PMF("Welcome! You are now logged in.")
                    IStatusMessage(self.request).addStatusMessage(msg, "info")
                    request_data = extract_request_data(self.request)
                    context_url = self.context.absolute_url()
                    redirect_url = request_data.get("next_url", context_url)
            except Exception as e:
                reason = _(str(e))
        else:
            reason = _("Invalid token or token expired.")

        if reason is not None:
            IStatusMessage(self.request).addStatusMessage(
                _("Setup failed! {0}".format(reason)), "error"
            )
            redirect_url = self.action()

        self.request.response.redirect(redirect_url)

    def updateFields(self, *args, **kwargs):
        """
        Bar code image is applied here.
        """
        disable_csrf_check()

        # Drop the "Login failed" message that appears because we consumed
        # the credentials in our authenticator plugin.
        request = self.request
        drop_login_failed_msg(request)

        user = self.user
        if user is not None:
            # Adding a proper description (with bar code image)
            self.description += (
                "<label>1. Scan this QR code with the Google Authenticator app</label>"
                + get_qr_code(user=user)
            )

            return super(SetupForm, self).updateFields(*args, **kwargs)
