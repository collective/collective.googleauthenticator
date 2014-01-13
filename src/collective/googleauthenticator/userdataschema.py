from zope.schema import Bool, TextLine
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from plone.app.users.userdataschema import IUserDataSchema, IUserDataSchemaProvider

_ = MessageFactory('collective.googleauthenticator')

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
        required=False,
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
