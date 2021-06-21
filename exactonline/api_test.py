# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
API tests.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2016-2021 Walter Doekes, OSSO B.V.
"""
import json
from time import time
from unittest import TestCase

from .api import ExactApi
from .http import opt_secure
from .storage import ExactOnlineConfig, MissingSetting

from .http_test import HttpTestResponse, HttpTestServer


# BEWARE: We disable security here! Don't import this unless you're
# running tests!
opt_secure.protocols = ('http', 'https')


class ApiTestCase(TestCase):
    class MemoryStorage(ExactOnlineConfig):
        def __init__(self, server_port, **kwargs):
            self._data = {
                'server': {
                    'auth_url': 'http://127.0.0.1:%d/auth' % (server_port,),
                    'rest_url': 'http://127.0.0.1:%d/api' % (server_port,),
                    'token_url': 'http://127.0.0.1:%d/token' % (server_port,),
                },
                'application': {
                    'client_id': 'CLIENT_ID',
                    'client_secret': 'CLIENT_SECRET',
                },
                'transient': {
                    'division': '1',
                    'access_token': 'ACCESS_TOKEN',
                    'refresh_token': 'REFRESH_TOKEN',
                },
            }
            for key, value in kwargs.items():
                self._data[key].update(**value)

        def get_division(self):
            return 1

        def get(self, section, option):
            if section not in self._data:
                raise MissingSetting(section, option)
            try:
                value = self._data[section][option]
            except KeyError:
                raise MissingSetting(section, option)
            return value

        def set(self, section, option, value):
            if section not in self._data:
                self._data[section] = {}
            self._data[section][option] = value

    def get_api(self, server_port):
        storage = self.MemoryStorage(server_port=server_port)

        # Set token expiry to 6 minutes, so we're not bothered by
        # autorefresh.
        storage.set_access_expiry(int(time()) + 360)

        return ExactApi(storage=storage)

    def test_call(self):
        data = {
            'd': {'results': [
                {'name': 'invoice1', 'identifier': 4},
                {'name': 'invoice2', 'identifier': 44},
            ]},
        }
        jsondata = json.dumps(data)

        server = HttpTestServer()
        server.add_response(HttpTestResponse('GET', '200', jsondata))
        server.start()

        api = self.get_api(server_port=server.port)
        res = api.invoices.filter(filter=u"Currency eq '\u20ac'", top=5)
        server.join()
        self.assertEqual(res, data['d']['results'])

    def test_autorefresh(self):
        data = {
            'd': {'results': [
                {'name': 'invoice1', 'identifier': 4},
                {'name': 'invoice2', 'identifier': 44},
            ]},
        }
        accesstoken = {
            'access_token': "AAEAAGxWulSxg7ZT-MPQMWOqQmssMzGa",
            'token_type': 'Bearer',
            'expires_in': 600,
            'refresh_token': 'Gcp7!IAAAABh4eI8DgkxRyGGyHPLLOz3y9Ss',
        }
        jsondata = json.dumps(data)
        jsonaccesstoken = json.dumps(accesstoken)

        # Set token expiry to 35 secs, no refresh yet.
        server = HttpTestServer()
        server.add_response(HttpTestResponse('GET', '200', jsondata))
        server.start()
        api = self.get_api(server_port=server.port)
        api.storage.set_access_expiry(int(time()) + 35)
        res = api.invoices.filter(filter=u"Currency eq '\u20ac'", top=5)
        server.join()
        self.assertEqual(res, data['d']['results'])

        # Set token expiry to 25 secs, automatic refresh.
        server = HttpTestServer()
        server.add_response(HttpTestResponse('POST', '200', jsonaccesstoken))
        server.add_response(HttpTestResponse('GET', '200', jsondata))
        server.start()
        api = self.get_api(server_port=server.port)
        api.storage.set_access_expiry(int(time()) + 25)
        self.assertLessEqual(api.storage.get_access_expiry(), time() + 25)
        res = api.invoices.filter(filter=u"Currency eq '\u20ac'", top=5)
        server.join()

        # New access token has been stored.
        self.assertEqual(
            api.storage.get_access_token(),
            'AAEAAGxWulSxg7ZT-MPQMWOqQmssMzGa')
        self.assertGreater(api.storage.get_access_expiry(), time() + 300)

        # And we still get the correct results.
        self.assertEqual(res, data['d']['results'])
