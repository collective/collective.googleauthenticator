"""
The helper module contains various methods for api security and for downloading files
"""
from hashlib import sha1
from uuid import uuid4
from urllib import urlencode, unquote, quote
from urlparse import urlparse
from urlparse import urlparse
import logging

from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory

from onetimepass import valid_totp

from plone.registry.interfaces import IRegistry
from plone import api

from ska import sign_url, validate_signed_request_data
import rebus

from collective.googleauthenticator.browser.controlpanel import IGoogleAuthenticatorSettings

_ = MessageFactory('collective.googleauthenticator')

logger = logging.getLogger("collective.googleauthenticator")

# ******************************************

def get_app_settings():
    """
    Gets the Google Authenticator settings.
    """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IGoogleAuthenticatorSettings)
    return settings

def get_user(username):
    """
    Get user by username given and return member object.
    """
    return api.user.get(username=username)

def get_username(user=None):
    """
    Gets the username of the user.

    :param user: If given, used to extract the user. Otherwise, ``plone.api.user.get_current`` is used.
    :return string:
    """
    if user is None:
        user = api.user.get_current()
    if user:
        return user.getUserName()

def get_base_url(request=None):
    """
    Gets domain name (with HTTP).

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    parsed_uri = urlparse(request.base)
    return "{0}://{1}/".format(parsed_uri.scheme, parsed_uri.netloc)

def get_domain_name(request=None):
    """
    Gets domain name (without HTTP).

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    parsed_uri = urlparse(request.base)
    return parsed_uri.netloc

def generate_secret(user):
    """
    Generates secret for the user.

    :param Products.PlonePAS.tools.memberdata user:
    """
    secret = rebus.b32encode(str(uuid4()))
    #logger.debug(secret)
    user.setMemberProperties(mapping={'two_factor_authentication_secret': secret,})
    return secret

def get_barcode_image(username, domain, secret):
    """
    Get barcode image URL.

    :param string username:
    :param string domain:
    :param string secret:
    :return string:
    """
    params = urlencode({
        'chs': '200x200',
        'chld': 'M|0',
        'cht': 'qr',
        'chl': "otpauth://totp/{0}@{1}?secret={2}".format(username, domain, secret)
        })
    url = "https://chart.googleapis.com/chart?{0}".format(params)
    return url

def get_secret(user=None, hashed=False):
    """
    Gets users' secret code. If ``hashed`` is set to True, returned hashed.

    :param Products.PlonePAS.tools.memberdata user:
    :param bool hashed: If set to True, hashed version is returned.
    :return string:
    """
    #TODO: Return hashed version if ``hashed`` is set to True.
    if user is None:
        user = api.user.get_current()
    if user:
        secret = user.getProperty('two_factor_authentication_secret')

        # If string returned, then it's likely a set string
        if isinstance(secret, basestring) and secret:
            return secret

def get_or_create_secret(user, overwrite=False):
    """
    Gets or creates token secret for the user given. Checks first if user given has a ``secret`` generated.
    If not, generate it for him and save it in his profile (``two_factor_authentication_secret``).

    :param Products.PlonePAS.tools.memberdata user: If provided, used. Otherwise ``plone.api.user.get_current``
        is used to obtain the user.
    :return string:
    """
    #TODO: Return hashed version if ``hashed`` is set to True.
    if user is None:
        user = api.user.get_current()

    if overwrite:
        return generate_secret(user)

    secret = user.getProperty('two_factor_authentication_secret')
    if isinstance(secret, basestring) and secret:
        return secret
    else:
        return generate_secret(user)

def get_token_description(user=None, overwrite_secret=False):
    """
    Gets description with bar code image.

    :param Products.PlonePAS.tools.memberdata user:
    :return string:
    """
    request = getRequest()

    if user is None:
        user = api.user.get_current()

    return """
        <div><img src="{url}" alt="QR Code" /></div>
    """.format(
        url = get_barcode_image(
            get_username(user),
            get_domain_name(request),
            get_or_create_secret(user, overwrite=overwrite_secret)
            ),
        )

def validate_token(token, user=None):
    """
    Validates the given token.

    :param string token:
    :return bool:
    """
    if user is None:
        user = api.user.get_current()

    secret = get_secret(user)

    #logger.debug('secret: {0}'.format(secret))

    validation_result = valid_totp(token=token, secret=secret)

    return validation_result

def get_browser_hash(request=None):
    """
    Gets browser hash. Adds an extra security layer, since browser version is unlikely to be changed.

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if request is None:
        request = getRequest()

    try:
        return sha1(request.get('HTTP_USER_AGENT')).hexdigest()
    except Exception as e:
        logger.debug(str(e))
        return ''

def get_ska_secret_key(request=None, user=None, use_browser_hash=True):
    """
    Gets the `secret_key` to be used in `ska` package.

    - Value of the ``two_factor_authentication_secret`` (from users' profile).
    - Browser info (hash of)
    - The SECRET set for the `ska` (use `plone.app.registry`).

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :param bool use_browser_hash: If set to True, browser hash is used. Otherwise - not. Defaults to True.
    :return string:
    """
    if request is None:
        request = getRequest()

    if user is None:
        user = api.user.get_current()

    settings = get_app_settings()

    ska_secret_key = settings.ska_secret_key

    user_secret = user.getProperty('two_factor_authentication_secret')

    if use_browser_hash:
        browser_hash = get_browser_hash(request=request)
    else:
        browser_hash = ''

    return "{0}{1}{2}".format(user_secret, browser_hash, ska_secret_key)

def is_two_factor_authentication_globally_enabled():
    """
    Checks if the two factor authentication is globally enabled.

    :return bool:
    """
    settings = get_app_settings()
    return settings.globally_enabled

def get_white_listed_ip_addresses():
    """
    Gets list of white-listed IP addresses.

    :return list:
    """
    settings = get_app_settings()
    ip_addresses = settings.ip_addresses_whitelist
    ip_addresses_list = ip_addresses.split('\n')
    return ip_addresses_list

def sign_user_data(request=None, user=None, url='@@google-authenticator-token'):
    """
    Signs the user data with `ska` package. The secret key is `secret_key` to be used with `ska` is a
    combination of:

    - Value of the ``two_factor_authentication_secret`` (from users' profile).
    - Browser info (hash of)
    - The SECRET set for the `ska` (use `plone.app.registry`).

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :param string url:
    :return string:
    """
    if request is None:
        request = getRequest()

    if user is None:
        user = api.user.get_current()

    # Make sure the secret key always exists
    get_or_create_secret(user)

    secret_key = get_ska_secret_key(request=request, user=user)
    signed_url = sign_url(
        auth_user = user.getUserId(),
        secret_key = secret_key,
        url = url
    )
    return signed_url

def extract_request_data_from_query_string(request_qs):
    """
    Plone seems to strip/escape some special chars (such as '+') from values and those chars are
    quite important for us. This method extracts the vars from request QUERY_STRING given and
    returns them unescaped.

    :FIXME: As stated above, for some reason Plone escapes from special chars from the values. If
    you know what the reason is and if it has some effects on security, please make the changes
    necessary.

    :param string request_qs:
    :return dict:
    """
    request_data = {}

    if not request_qs:
        return request_data

    for part in request_qs.split('&'):
        try:
            key, value = part.split('=', 1)
            request_data.update({key: unquote(value)})
        except ValueError as e:
            pass

    return request_data

def extract_request_data(request):
    """
    Plone seems to strip/escape some special chars (such as '+') from values and those chars are
    quite important for us. This method extracts the vars from request QUERY_STRING given and
    returns them unescaped.

    :FIXME: As stated above, for some reason Plone escapes from special chars from the values. If
    you know what the reason is and if it has some effects on security, please make the changes
    necessary.

    :param request ZPublisher.HTTPRequest:
    :return dict:
    """
    request_qs = request.get('QUERY_STRING')
    return extract_request_data_from_query_string(request_qs)

def extract_next_url_from_referer(request, quote_url=False):
    """
    Since we override the default Plone functionality (take out the `came_from` from the login form for a
    very strong reason), we want to make sure that for users, the "came from" functionality stays intact.
    That why, we check the referer for the `came_from` attributes and if present, redirect to that after
    successful two-factor authentication token validation.
    :param request ZPublisher.HTTPRequest:
    :return string: Extracted `came_from` URL.
    """
    referer = request.get('HTTP_REFERER')
    request_qs = urlparse(referer).query
    request_data = extract_request_data_from_query_string(request_qs)
    url = request_data.get('came_from', '')

    if quote_url:
        return quote(url)

    return url

def validate_user_data(request, user, use_browser_hash=True):
    """
    Validates the user data.

    :param ZPublisher.HTTPRequest request:
    :param Products.PlonePAS.tools.memberdata user:
    :return ska.SignatureValidationResult:
    """
    secret_key = get_ska_secret_key(request=request, user=user, use_browser_hash=use_browser_hash)
    validation_result = validate_signed_request_data(
        data = extract_request_data(request),
        secret_key = secret_key
        )
    return validation_result

def has_enabled_two_factor_authentication(user):
    """
    Checks if user has enabled the two-step verification.

    :param Products.PlonePAS.tools.memberdata user:
    :return bool:
    """
    if bool(api.user.is_anonymous()) is True:
        return None

    try:
        return user.getProperty('enable_two_factor_authentication', False)
    except Exception as e:
        return None

def enable_two_factor_authentication_for_users(users=[]):
    """
    Enable two-factor authentication for the list of users given.
    """
    if not users:
        users = api.user.get_users()

    for user in users:
        try:
            get_or_create_secret(user)
            if not has_enabled_two_factor_authentication(user):
                user.setMemberProperties(mapping={'enable_two_factor_authentication': True,})
        except Exception as e:
            logger.debug(str(e))

def disable_two_factor_authentication_for_users(users=[]):
    """
    Disable two-factor authentication for the list of users given.
    """
    if not users:
        users = api.user.get_users()

    for user in users:
        try:
            #get_or_create_secret(user)
            if has_enabled_two_factor_authentication(user):
                user.setMemberProperties(mapping={'enable_two_factor_authentication': False,})
        except Exception as e:
            logger.debug(str(e))

def extract_ip_address_from_request(request=None):
    """
    Extracts client's IP address from request. This is not the safest solution, since client
    may change headers.

    :param ZPublisher.HTTPRequest request:
    :return string:
    """
    if not request:
        request = getRequest()

    PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', )
    ip = request.get('REMOTE_ADDR')
    x_forwarded_for = request.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        proxies = [proxy.strip() for proxy in x_forwarded_for.split(',')]

        # Remove the private ips from the beginning
        while (len(proxies) > 0 and proxies[0].startswith(PRIVATE_IPS_PREFIX)):
            proxies.pop(0)

        # Take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip

def get_ip_addresses_whitelist(request=None):
    """
    Gets IP addresses white list.

    :param ZPublisher.HTTPRequest request:
    :return list:
    """
    if not request:
        request = getRequest()

    settings = get_app_settings()

    ip_addresses_whitelist = settings.ip_addresses_whitelist

    if ip_addresses_whitelist:
        try:
            ip_addresses_whitelist = ip_addresses_whitelist.split('\n')
            ip_addresses_whitelist = [ip_address.strip() for ip_address in ip_addresses_whitelist]
        except Exception as e:
            logger.debug(str(e))
            ip_addresses_whitelist = []

    return ip_addresses_whitelist or []

def is_whitelisted_client(request=None):
    """
    Checks if client's IP address is whitelisted.

    :param ZPublisher.HTTPRequest request:
    :return bool:
    """
    ip_addresses_whitelist = get_ip_addresses_whitelist(request=request)

    ip_address = extract_ip_address_from_request(request=request)

    if ip_address in ip_addresses_whitelist:
        return True

    return False
