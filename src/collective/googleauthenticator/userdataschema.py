import logging

from plone import api

from zope.component import adapter
from zope.schema import Bool, TextLine
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from plone.app.users.userdataschema import IUserDataSchema, IUserDataSchemaProvider
from plone.app.users.browser.personalpreferences import UserDataPanel

from Products.PluggableAuthService.interfaces.authservice import IBasicUser
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent

logger = logging.getLogger("collective.googleauthenticator")

_ = MessageFactory('collective.googleauthenticator')

class CustomizedUserDataPanel(UserDataPanel):
    """
    Customise the user form shown in personal-preferences.
    """
    def __init__(self, context, request):
        super(CustomizedUserDataPanel, self).__init__(context, request)

        # Removing certain fields from form
        self.form_fields = self.form_fields.omit(
            'enable_two_factor_authentication',
            'two_factor_authentication_secret',
            'bar_code_reset_token',
            )


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema


class IEnhancedUserDataSchema(IUserDataSchema):
    """
    Extended user profile.

    :property bool enable_two_factor_authentication: Indicates, whether the two-step verification is
                                                     enabled for the user.
    :property string two_factor_authentication_secret: Secret key of the user (unique per user). Automatically
                                                       generated.
    :property string bar_code_reset_token: Token to reset users' bar-code. Automatically generated.
    """
    enable_two_factor_authentication = Bool(
        title=_('Enable two-step verification.'),
        description=_("""Enable/disable the two-step verification. Click <a href=\"@@setup-two-factor-authentication\"> """
                      """here</a> to set it up or <a href=\"@@disable-two-factor-authentication\">here</a> to """
                      """disable it."""
            ),
        required=False
        )

    two_factor_authentication_secret = TextLine(
        title = _('Secret key'),
        description = _('Automatically generated'),
        required = False,
    )

    bar_code_reset_token = TextLine(
        title = _('Token to reset the bar code'),
        description = _('Automatically generated'),
        required = False,
    )


@adapter(IBasicUser, IPrincipalCreatedEvent)
def userCreatedHandler(principal, event):
    """
    Fired upon creation of each user. If app setting ``globally_enabled`` is set to True,
    two-step verification would be automatically enabled for the registered users (in that
    case they would have to go through the bar-code recovery procedure.

    The ``principal`` value is seems to be a user object, although it does not have
    the ``setMemberProperties`` method defined (that's why we obtain the user
    using `plone.api`, 'cause that one has it).
    """
    from collective.googleauthenticator.helpers import (
        is_two_factor_authentication_globally_enabled, get_or_create_secret
        )
    user = api.user.get(username=principal.getId())
    if is_two_factor_authentication_globally_enabled():
        get_or_create_secret(user)
        user.setMemberProperties(mapping={'enable_two_factor_authentication': True,})

    logger.debug(user.getProperty('enable_two_factor_authentication'))
    logger.debug(user.getProperty('two_factor_authentication_secret'))
