# vim: set ts=8 sw=4 sts=4 et ai tw=79:
from ..http import HTTPError


class Autorefresh(object):
    def rest(self, method, resource, data=None):
        try:
            decoded = super(Autorefresh, self).rest(method, resource, data=data)
        except HTTPError, e:
            if e.code != 401:
                raise

            # Refresh token.
            self.refresh_token()

            # Retry.
            decoded = super(Autorefresh, self).rest(method, resource, data=data)

        return decoded
