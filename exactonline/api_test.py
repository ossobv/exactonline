# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
API tests.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2016 Walter Doekes, OSSO B.V.
"""
import json
from unittest import TestCase

from .api import ExactApi
from .http import opt_secure
from .storage import ExactOnlineConfig

from .http_test import HttpTestServer


# BEWARE: We disable security here! Don't import this unless you're
# running tests!
opt_secure.protocols = ('http', 'https')


class ApiTestCase(TestCase):
    class MemoryStorage(ExactOnlineConfig):
        def __init__(self, server_port, **kwargs):
            self._data = {
                'api_url': 'http://127.0.0.1:%d/api' % (server_port,),
                'client_id': 'CLIENT_ID',
                'client_secret': 'CLIENT_SECRET',
                'division': 1,
                'iteration_limit': 50,
                'auth': {
                    'access_token': 'ACCESS_TOKEN',
                    'refresh_token': 'REFRESH_TOKEN',
                },
            }
            for key, value in kwargs.items():
                self._data[key].update(**value)

        def get_division(self):
            return 1

        def __getitem__(self, k):
            if k not in self._data:
                raise Exception(f"Cannot find {k}")
            try:
                value = self._data.__getitem__(k)
            except KeyError:
                raise Exception(f"Cannot find {k}")
            return value

        def __setitem__(self, k, v):
            self._data.__setitem__(k, v)

    def get_api(self, server_port):
        storage = self.MemoryStorage(server_port=server_port)
        return ExactApi(storage=storage)

    def test_call(self):
        data = {
            'd': {'results': [
                {'name': 'invoice1', 'identifier': 4},
                {'name': 'invoice2', 'identifier': 44},
            ]},
        }
        jsondata = json.dumps(data)
        server = HttpTestServer('GET', '200', jsondata)
        api = self.get_api(server_port=server.port)
        res = api.invoices.filter(filter=u"Currency eq '\u20ac'", top=5)
        server.join()
        self.assertEqual(res, data['d']['results'])
