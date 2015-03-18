# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Looks for __next values, and begins to download those documents
automatically; it unpaginates resultsets.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""


class Unwrap(object):
    def rest(self, method, resource, data=None, recursion=0):
        if recursion > 50:
            raise ValueError('Recursion limit reached! Last resource %r' %
                             (resource,))

        decoded = super(Unwrap, self).rest(method, resource, data=data)

        # DELETE and PUT methods return None.
        if not decoded:
            return decoded

        # GET/POST methods return a host of different types.
        data = decoded.pop(u'd', None)
        if data is None or decoded:
            raise ValueError('Expected *only* "d" in response, got this: '
                             'response=%r, d=%r' % (decoded, data))

        # POST methods return a nice dictionary inside of 'd'.
        if method == 'POST':
            return data

        # GET methods...
        if isinstance(data, dict):
            ret = self._rest_with_next(data, method, resource, recursion)

        elif isinstance(data, list):
            ret = data

        else:
            raise ValueError(
                'Expected *list* or *dict* in "d", got this: d=%r' % (data,))

        return ret

    def _rest_with_next(self, result_data, method, resource, recursion):
        results = result_data.pop(u'results', None)
        next_ = result_data.pop(u'__next', None)
        if results is None or result_data:
            raise ValueError('Expected *only* "results" in "d", got this: '
                             'd=%r, results=%r' % (result_data, results))

        ret = results
        assert isinstance(ret, list)

        # If there is more data to fetch, do that.
        if next_ is not None:
            if method != 'GET':
                raise ValueError(
                    'Got *more* data for non-GET request: '
                    'method=%s, resource=%r, next=%r, data=%r' %
                    (method, resource, next_, result_data))

            # TODO: We don't want to use recursion for this, but a nice
            # forloop which calls super().rest() directly.
            results = self.rest('GET', next_, recursion=(recursion + 1))
            ret.extend(results)

        return ret
