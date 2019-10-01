# coding=utf-8
from plone import api
from Products.PluggableAuthService.interfaces.authservice import IBasicUser
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.schema import Bool
from zope.schema import TextLine

import logging


logger = logging.getLogger("collective.googleauthenticator")

_ = MessageFactory('collective.googleauthenticator')


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
