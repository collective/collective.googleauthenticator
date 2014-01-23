from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

_ = MessageFactory('collective.googleauthenticator')

class DisableTwoFactorAuthentication(BrowserView):
    """
    Disabling the two-step verification.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def disable(self):
        """
        Disable the two-step verification for the user and redirect back to the `@@personal-information`.
        """
        if bool(api.user.is_anonymous()) is True:
            self.request.response.setStatus(401, _('Forbidden for anonymous'), True)
            return None

        user = api.user.get_current()
        user.setMemberProperties(
            mapping = {
                'enable_two_factor_authentication': False,
                'two_factor_authentication_secret': '',
                'bar_code_reset_token': ''
                }
            )

        IStatusMessage(self.request).addStatusMessage(
            _("You have successfully disabled the two-step verification for your account."),
            'info'
            )
        redirect_url = "{0}/@@personal-information".format(self.context.absolute_url())
        self.request.response.redirect(redirect_url)
