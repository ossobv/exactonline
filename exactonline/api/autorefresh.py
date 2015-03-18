# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Refreshes OAuth tokens as-needed on receiving a 401.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from ..http import HTTPError


class Autorefresh(object):
    def rest(self, method, resource, data=None):
        try:
            decoded = super(Autorefresh, self).rest(method, resource, data=data)
        except HTTPError as e:
            if e.code != 401:
                raise

            # Refresh token.
            self.refresh_token()

            # Retry.
            decoded = super(Autorefresh, self).rest(method, resource, data=data)

        return decoded
