# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Refreshes OAuth tokens in a timely manner.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2021 Walter Doekes, OSSO B.V.
"""
from time import time

from ..http import HTTPError


class Autorefresh(object):
    """
    Refresh OAuth token in a timely manner

    Docs: https://support.exactonline.com/community/s/knowledge-base
      #All-All-DNO-Content-oauth-eol-oauth-devstep3

    > **Do not request a new access token too late**
    > Use your refresh token to get a new access token before it
    > expires. If you make an API call with an expired access token, your
    > call will be rejected with response code 401 and reason
    >
    > **Do not request a new access token too early**
    > You should only request a new token right before it expires. You
    > can only request a new access token 9 minutes and 30 seconds after
    > you received it. If you request an access token before the 9 minutes
    > and 30 seconds have passed, your call will be rejected with response
    > code 401 and reason Access Token not expired.

    Apparently waiting for a 401 is frowned upon. So instead we'll wait
    until there are fewer than 30 seconds left and then ask for a new
    token.

    If we still get a 401, we'll _also_ do a token refresh and hope that the
    disagreement between us and the server gets resolved.
    """
    def raw_rest(self, request):
        # Check how much time we have left, and refresh token 30 seconds before
        # it expires.
        have_fresh_token = False
        token_expiry = self.storage.get_access_expiry()
        time_left_before_expiry = (token_expiry - time())
        if time_left_before_expiry < 30:
            self.refresh_token()
            have_fresh_token = True

        try:
            response = super(Autorefresh, self).raw_rest(request)
        except HTTPError as e:
            if e.code == 401 and not have_fresh_token:
                # If we received a 401 even though we think our token is
                # still valid, maybe we were wrong about the expiry
                # time. (Maybe one of the clocks is off, maybe the
                # remote side flushed the tokens.)
                self.refresh_token()

                # Retry the call but don't catch additional 401s.
                response = super(Autorefresh, self).raw_rest(request)

            else:
                raise

        return response
