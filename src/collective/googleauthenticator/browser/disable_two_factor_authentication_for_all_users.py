from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from collective.googleauthenticator.helpers import disable_two_factor_authentication_for_users

_ = MessageFactory('collective.googleauthenticator')

class DisableTwoFactorAuthenticationForAllUsers(BrowserView):
    """
    Disable the two-step verification for all users.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def index(self):
        """
        Disble the two-step verification for the user and redirect back to the `@@google-authenticator-settings`.
        """
        users = api.user.get_users()
        disable_two_factor_authentication_for_users(users)

        IStatusMessage(self.request).addStatusMessage(
            _("You have successfully disabled the two-step verification for all users."),
            'info'
            )
        redirect_url = "{0}/@@google-authenticator-settings".format(self.context.absolute_url())
        self.request.response.redirect(redirect_url)
