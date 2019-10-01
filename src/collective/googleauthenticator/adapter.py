import logging

from zope.interface import Interface, implements

from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from collective.googleauthenticator.helpers import extract_next_url_from_referer

logger = logging.getLogger(__file__)

class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    Adapter for `collective.googleauthenticator.userdataschema.IEnhancedUserDataSchema`.
    """
    # ****************************************************
    # ******* ``enable_two_step_verification`` *******
    # ****************************************************
    def get_enable_two_factor_authentication(self):
        return self.context.getProperty('enable_two_factor_authentication', '')

    def set_enable_two_factor_authentication(self, value):
        return # Read only
        #return self.context.setMemberProperties({'enable_two_factor_authentication': value})

    enable_two_factor_authentication = property(
        get_enable_two_factor_authentication,
        set_enable_two_factor_authentication
        )

    # ****************************************************
    # ********** ``two_factor_auth_secret_key`` **********
    # ****************************************************
    def get_two_factor_authentication_secret(self):
        return self.context.getProperty('two_factor_authentication_secret', '')

    def set_two_factor_authentication_secret(self, value):
        return # Read only
        #return self.context.setMemberProperties({'two_factor_authentication_secret': value})

    two_factor_authentication_secret = property(
        get_two_factor_authentication_secret,
        set_two_factor_authentication_secret
        )

    # ****************************************************
    # *************** ``bar_code_reset_token`` ***********
    # ****************************************************
    def get_bar_code_reset_token(self):
        return self.context.getProperty('bar_code_reset_token', '')

    def set_bar_code_reset_token(self, value):
        return # Read only
        #return self.context.setMemberProperties({'bar_code_reset_token': value})

    bar_code_reset_token = property(
        get_bar_code_reset_token,
        set_bar_code_reset_token
        )


class ICameFrom(Interface):
    """
    Interface for getting the ``came_from`` URL.
    """


class CameFromAdapter(object):
    """
    Came from handling.

    Plone `came_from` field had to be taken out of the login form, so that users always get the
    token validation screen, prior to being redirected to page they came from. The came_from
    is instead extracted from referer and handled in such a way, that Plone functionality stays
    intact.

    In cases your existing package smuggles with `came_from` (for example, you want users first
    to accept terms and conditions prior redirection), you would likely need to define
    a new adapter and make appropriate changes to the ``getCameFrom`` method.

    :example:
    >>> from zope.interface import implements
    >>> from plone import api
    >>> from collective.googleauthenticator.helpers import extract_next_url_from_referer
    >>> from collective.googleauthenticator.adapter import ICameFrom
    >>> 
    >>> class CameFromAdapter(object):
    >>>     implements(ICameFrom)
    >>> 
    >>>     def __init__(self, request):
    >>>         self.request = request
    >>> 
    >>>     def getCameFrom(self):
    >>>         real_referrer = extract_next_url_from_referer(self.request)
    >>>         portal = api.portal.get()
    >>>         if not real_referrer:
    >>>             real_referrer = portal.absolute_url()
    >>>         referrer = "{0}/tac-form/?came_from={1}".format(portal.portal_url(), real_referrer)
    >>>         return referrer
    """
    implements(ICameFrom)

    def __init__(self, request):
        """
        :param request ZPublisher.HTTPRequest:
        """
        self.request = request

    def getCameFrom(self):
        """
        Extracts the ``came_from`` value from the referrer (uses global request).

        :return string:
        """
        return extract_next_url_from_referer(self.request)
