from zope.i18nmessageid import MessageFactory

from plone import api

from Products.Five import BrowserView

from collective.googleauthenticator.helpers import (
    is_two_factor_authentication_globally_enabled, has_enabled_two_factor_authentication
    )

_ = MessageFactory('collective.googleauthenticator')

class SettingsHelper(BrowserView):
    """
    Helper view for accessing some conditions from portal actions (actions.xml).
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_two_factor_authentication_globally_enabled(self):
        """
        Disable the two-step verification for the user and redirect back to the `@@personal-information`.
        """
        return is_two_factor_authentication_globally_enabled()

    def show_enable_two_factor_authentication_link(self):
        """
        Indicates whether the enable two factor authentication link should be shown.

        The following conditions shall be met for True to be returned:

        - User hasn't enabled the two factor authentication for his account.
        - In app settings, the globally enable two factor authentication is set to False.

        :return bool:
        """
        user = api.user.get_current()
        return not is_two_factor_authentication_globally_enabled() \
               and (has_enabled_two_factor_authentication(user) is False)

    def show_disable_two_factor_authentication_link(self):
        """
        Indicates whether the disable two factor authentication link should be shown.

        The following conditions shall be met for True to be returned:

        - User hasn enabled the two factor authentication for his account.
        - In app settings, the globally enable two factor authentication is set to False.

        :return bool:
        """
        user = api.user.get_current()
        return not is_two_factor_authentication_globally_enabled() and has_enabled_two_factor_authentication(user)
