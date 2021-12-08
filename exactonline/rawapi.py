# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Base API interface.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2021 Walter Doekes, OSSO B.V.
"""
import json
import logging
import os
import sys

from time import sleep, time

from .http import HTTPError, Options, opt_secure, http_req, binquote, urljoin


logger = logging.getLogger(__name__)


def _json_safe(data):
    """
    json.loads wants an unistr in Python3. Convert it.
    """
    if not hasattr(data, 'encode'):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(
                'Expected valid UTF8 for JSON data, got %r' % (data,))
    return data


class RateLimiter(object):
    """
    Keep track of ratelimits as imposed by ExactOnline.

    If we ignore these, we'll run into a 429 Too Many Requests.

    The ExactRawApi class calls .backoff() to (a) wait and (b) check
    whether waiting was necessary.

    The http_req method calls .update() to update the current rate limit
    values as provided by the API server.

    NOTE: ExactOnline keeps a timer _per_ division. But this limiter updates
    automatically, so that is not much of a problem.
    """
    def __init__(self):
        self._reset_times = {}

    def backoff(self):
        """
        Check if we need to wait, and wait. Returns True if we did any waiting.
        """
        seconds = self._should_wait()
        if seconds > 0:
            self.wait(seconds)
            return True
        return False

    def wait(self, seconds):
        """
        Handle the actual waiting and print a notice to the user.
        """
        assert seconds > 0, seconds

        if sys.stderr and os.isatty(sys.stderr.fileno()):
            sys.stderr.write(
                '(sleeping for {} seconds because of ratelimits {!r})\n'
                .format(seconds, self))

        logger.info(
            'Sleeping for %d seconds because of ratelimits %r',
            seconds, self)

        sleep(seconds)

    def update(self, until, limit, remaining):
        until = int(until)
        limit = int(limit)
        remaining = int(remaining)
        assert 1638448971000 < until < 9999999999999, until
        assert limit >= 0, limit
        assert remaining >= 0, remaining
        until //= 1000  # store per second, not millisecond
        # minutely and daily might overlap. Should not be an issue if we
        # update() the shortest value last (first Daily, then Minutely).
        self._reset_times[until] = (limit, remaining)

    def _clean(self):
        now = int(time())
        for key in list(self._reset_times.keys()):
            if key < now:
                del self._reset_times[key]

    def _should_wait(self):
        self._clean()
        # 0.5s offset, copes with slight clock drift AND ensures we get a
        # non-zero wait right after a 429.
        now = int(time() - 0.5)
        wait_until = None
        amount_left = None
        for key in self._reset_times:
            if now < key:
                if wait_until is None:
                    wait_until = key
                    amount_left = self._reset_times[key][1]
                elif amount_left > self._reset_times[key][1]:
                    wait_until = key
                    amount_left = self._reset_times[key][1]

        if wait_until is not None and amount_left < 1:
            return max((wait_until - now), 0)

        return 0

    def __repr__(self):
        return '<RateLimiter({}, {!r})>'.format(
            int(time()), self._reset_times)


class ExactRawApi(object):
    def __init__(self, storage, **kwargs):
        super(ExactRawApi, self).__init__(**kwargs)
        self.storage = storage
        self.limiter = self.get_ratelimiter()

    def get_ratelimiter(self):
        """
        Create a RateLimiter instance. Override this if you want non-default
        rate limiting behaviour.

        TODO: Consider moving the default RateLimiter to a separate Mixin?
        """
        return RateLimiter()

    def create_auth_request_url(self):
        # Build the URLs manually so we get consistent order.
        auth_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'redirect_uri': binquote(self.storage.get_response_url()),
            'response_type': 'code',  # or 'token' for JS apps
        }
        auth_data = ('client_id=%(client_id)s'
                     '&redirect_uri=%(redirect_uri)s'
                     '&response_type=%(response_type)s' %
                     auth_params)

        url = '?'.join([self.storage.get_auth_url(), auth_data])
        logger.debug('Created auth request URL {url}'.format(url=url))
        return url

    def request_token(self, code):
        logger.debug('Requesting a new token')
        # Build the URLs manually so we get consistent order.
        token_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'client_secret': binquote(self.storage.get_client_secret()),
            'code': binquote(code),
            'grant_type': 'authorization_code',
            'redirect_uri': binquote(self.storage.get_response_url()),
        }
        token_data = ('client_id=%(client_id)s'
                      '&client_secret=%(client_secret)s'
                      '&code=%(code)s'
                      '&grant_type=%(grant_type)s'
                      '&redirect_uri=%(redirect_uri)s' %
                      token_params)

        # Fire away!
        url = self.storage.get_token_url()
        response = _json_safe(http_req(
            'POST', url, token_data, opt=opt_secure, limiter=self.limiter))

        # Validate and store the values.
        self._set_tokens(response)
        # Store the code first after _set_tokens() has validated the
        # data. We don't want to store some bogus code fed to use by Joe
        # Random user.
        self.storage.set_code(code)

    def refresh_token(self):
        logger.debug('Refreshing token')
        # Bring on the fresh stuff. This needs to be called 30 seconds before
        # token expiry. Or after a 401. See the Autorefresh mixin.

        # Build the URLs manually so we get consistent order.
        refresh_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'client_secret': binquote(self.storage.get_client_secret()),
            'grant_type': 'refresh_token',
            'refresh_token': binquote(self.storage.get_refresh_token()),
        }
        refresh_data = ('client_id=%(client_id)s'
                        '&client_secret=%(client_secret)s'
                        '&grant_type=%(grant_type)s'
                        '&refresh_token=%(refresh_token)s' %
                        refresh_params)

        # Fire away!
        url = self.storage.get_refresh_url()
        response = _json_safe(http_req(
            'POST', url, refresh_data, opt=opt_secure, limiter=self.limiter))

        # Validate and store the values.
        self._set_tokens(response)

    def rest(self, request):
        # Don't pass "/api" in the resource, it's in the base URL already!
        # And don't start with a slash either, since we use urljoin on it.
        #
        # See this for a list of possible resources.
        # https://start.exactonline.co.uk/docs/HlpRestAPIResources.aspx
        url = urljoin(
            self.storage.get_rest_url().rstrip('/') + '/', request.resource)

        # Convert data to json.
        if request.data is None:
            data = None
        elif isinstance(request.data, str):
            data = request.data
        else:
            data = json.dumps(request.data)

        new_request = request.update(resource=url, data=data)

        response = self._rest_query(new_request)

        if request.method in ('DELETE', 'PUT'):
            if response != '':
                raise ValueError(
                    'Expected empty data for %s operation: '
                    'resource=%r, returned=%r' % (
                        request.method, request.resource, response))
            decoded = None
        else:
            try:
                decoded = json.loads(response)
            except ValueError:
                raise ValueError(
                    'Expected valid JSON data for %s operation: '
                    'resource=%r, returned=%r' % (
                        request.method, request.resource, response))

        return decoded

    def _rest_query(self, request):
        self.limiter.backoff()

        token = self.storage.get_access_token()
        opt_custom = Options()
        opt_custom.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % (token,),
        }
        if request.method in ('POST', 'PUT'):
            opt_custom.headers.update({'Content-Type': 'application/json'})
        opt = (opt_secure | opt_custom)

        try:
            response = http_req(
                request.method, request.resource, data=request.data,
                opt=opt, limiter=self.limiter)
        except HTTPError as e:
            if e.getcode() == 429 and self.limiter.backoff():
                response = http_req(
                    request.method, request.resource, data=request.data,
                    opt=opt, limiter=self.limiter)
            else:
                raise

        return _json_safe(response)

    def _set_tokens(self, jsondata):
        logger.debug('Update tokens with newly retrieved token data')
        # The json should look somewhat like this:
        # {"access_token":"AAEA..",
        #  "token_type":"bearer",
        #  "expires_in":"600",
        #  "refresh_token":"__1P!I.."}
        decoded = json.loads(jsondata)

        # Validate the values.
        assert decoded.get('access_token'), decoded
        expires_in = int(decoded.get('expires_in', '0'))
        assert expires_in > 0, decoded
        assert decoded.get('refresh_token'), decoded
        assert decoded.get('token_type', '').lower() == 'bearer', decoded

        # Store the values.
        self.storage.set_access_expiry(int(time()) + expires_in)
        self.storage.set_access_token(decoded['access_token'])
        self.storage.set_refresh_token(decoded['refresh_token'])
