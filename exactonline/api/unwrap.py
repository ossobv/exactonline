# vim: set ts=8 sw=4 sts=4 et ai tw=79:


class Unwrap(object):
    def rest(self, method, resource, data=None, recursion=0):
        if recursion > 50:
            raise ValueError('Recursion limit reached! Last resource %r' % (resource,))

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
            results = data.pop(u'results', None)
            next = data.pop(u'__next', None)
            if results is None or data:
                raise ValueError('Expected *only* "results" in "d", got this: '
                                 'd=%r, results=%r' % (data, results))

            ret = results
            assert isinstance(ret, list)

            # If there is more data to fetch, do that.
            if next is not None:
                if method != 'GET':
                    raise ValueError('Got *more* data for non-GET request: '
                                     'method=%s, resource=%r, next=%r, results=%r' %
                                     (method, resource, next, results))

                results = self.rest('GET', next, recursion=(recursion + 1))
                ret.extend(results)

        elif isinstance(data, list):
            ret = data

        else:
            raise ValueError('Expected *list* or *dict* in "d", got this: d=%r' % (data,))

        return ret
