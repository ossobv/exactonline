# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
HTTP shortcuts, taken from osso-djuty.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.

We may want to replace this with something simpler.
"""
import urllib
import socket
import ssl
import sys

from os import path
from unittest import TestCase, main, skip

try:
    from http.client import HTTPConnection, HTTPS_PORT
except ImportError:  # python2
    from httplib import HTTPConnection, HTTPS_PORT
try:
    from urllib import request
except ImportError:  # python2
    import urllib2 as request
try:
    from urllib.parse import urljoin
except ImportError:  # python2
    from urlparse import urljoin


# ; helpers

def binquote(value):
    """
    We use quote() instead of urlencode() because the Exact Online API
    does not like it when we encode slashes -- in the redirect_uri -- as
    well (which the latter does).
    """
    return urllib.quote(value.encode('utf-8'))

urljoin  # touch it, we don't use it


# ; http stuff

class BadProtocol(ValueError):
    """
    Raised when you try to http_get or http_post with a disallowed
    protocol.
    """
    pass


class HTTPError(request.HTTPError):
    """
    Override the original HTTPError, drop the fp and add a response.
    """
    def __init__(self, url, code, msg, hdrs, response):
        request.HTTPError.__init__(self, url, code, msg, hdrs, None)
        self.response = response

    def __str__(self):
        if not isinstance(self.response, str):
            response = self.response.decode('utf-8', 'replace')
        else:
            response = self.response
        response = response[0:512] + ('', '...')[len(response) > 512]
        response = ''.join(('?', i)[0x20 <= ord(i) <= 0x7F or i in '\t\n\r']
                           for i in response)
        return 'PENA'
        return ('HTTPError: """%s %s\nContent-Type: %s\n'
                'Content-Length: %d\n\n%s"""' %
                (self.code, self.msg, self.hdrs.type, len(self.response),
                 response))


class Options(object):
    # Which protocols to we allow.
    protocols = ('http', 'https')
    # Do we validate the SSL certificate.
    verify_cert = False
    # What we use to validate the SSL certificate.
    cacert_file = '/etc/ssl/certs/ca-certificates.crt'
    # Optional headers.
    headers = None

    # Which properties we have.
    _PROPERTIES = ('protocols', 'verify_cert', 'cacert_file', 'headers')

    def __or__(self, other):
        """
        Join multiple Options together with the or-operator '|'.
        It uses the identity operator to compare values against the
        default values, so non-overridden values won't overwrite
        overridden ones.

        BUG: This will fail if you try to re-set booleans from False
        to True to False.
        """
        new_options = Options()

        for source in (self, other):
            for item in self._PROPERTIES:
                source_item = getattr(source, item)
                if source_item is not getattr(Options, item):  # identity check
                    setattr(new_options, item, source_item)

        return new_options

# Default options.
opt_default = Options()

# SSL-safe options.
opt_secure = Options()
opt_secure.protocols = ('https',)
opt_secure.verify_cert = True


class Request(request.Request):
    """
    Override the request.Request class to supply a custom method.
    """
    def __init__(self, method=None, *args, **kwargs):
        request.Request.__init__(self, *args, **kwargs)
        assert method in ('DELETE', 'GET', 'POST', 'PUT')
        self._method = method

    def get_method(self):
        return self._method


class ValidHTTPSConnection(HTTPConnection):
    """
    This class allows communication via SSL.

    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    default_port = HTTPS_PORT
    cacert_file = opt_default.cacert_file

    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, ca_certs=self.cacert_file,
                                    cert_reqs=ssl.CERT_REQUIRED)


class ValidHTTPSHandler(request.HTTPSHandler):
    """
    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    def __init__(self, cacert_file):
        self.cacert_file = cacert_file
        request.HTTPSHandler.__init__(self)

    def https_open(self, req):
        # If someone uses an alternate cacert_file, we have no decent
        # way of telling that to a subclass (not instance).
        if self.cacert_file == ValidHTTPSConnection.cacert_file:
            class_ = ValidHTTPSConnection
        else:
            # Yuck. Create a local subclass so we can set a custom
            # cacert_file.
            class CustomValidHTTPSConnection(ValidHTTPSConnection):
                cacert_file = self.cacert_file
            class_ = CustomValidHTTPSConnection

        return self.do_open(class_, req)


def http_delete(url, opt=opt_default):
    '''
    Shortcut for urlopen (GET) + read. We'll probably want to add a nice
    timeout here later too.
    '''
    return _http_request(url, method='DELETE', opt=opt)


def http_get(url, opt=opt_default):
    '''
    Shortcut for urlopen (GET) + read. We'll probably want to add a nice
    timeout here later too.
    '''
    return _http_request(url, method='GET', opt=opt)


def http_post(url, data=None, opt=opt_default):
    '''
    Shortcut for urlopen (POST) + read. We'll probably want to add a
    nice timeout here later too.
    '''
    if isinstance(data, str):
        # Allow binstrings for data.
        pass
    elif data:
        data = urllib.urlencode(data)
    else:
        data = ''.encode('utf-8')  # ensure POST-mode
    return _http_request(url, method='POST', data=data, opt=opt)


def http_put(url, data=None, opt=opt_default):
    '''
    Shortcut for urlopen (PUT) + read. We'll probably want to add a
    nice timeout here later too.
    '''
    if isinstance(data, str):
        # Allow binstrings for data.
        pass
    elif data:
        data = urllib.urlencode(data)
    else:
        data = ''.encode('utf-8')  # ensure POST-mode
    return _http_request(url, method='PUT', data=data, opt=opt)


def _http_request(url, method=None, data=None, opt=None):
    # Check protocol.
    proto = url.split(':', 1)[0]
    if proto not in opt.protocols:
        raise BadProtocol('Protocol %s in URL %r disallowed by caller' %
                          (proto, url))

    # Create URL opener.
    if opt.verify_cert:
        # It's legal to pass either a class or an instance here.
        opener = request.build_opener(ValidHTTPSHandler(opt.cacert_file))
    else:
        opener = request.build_opener()

    # Create the Request with optional extra headers.
    req = Request(url=url, data=data, method=method,
                  headers=(opt.headers or {}))

    exc_info, fp, stored_exception = None, None, None
    try:
        fp = opener.open(req)
        # print fp.info()  # (temp, print headers)
        response = fp.read()
    except request.HTTPError as exception:
        fp = exception.fp  # see finally clause
        exc_info = sys.exc_info()
        stored_exception = exception
    except Exception as exception:
        exc_info = sys.exc_info()
        stored_exception = exception
    finally:
        if fp:
            # Try a bit harder to flush the connection and close it
            # properly. In case of errors, our django testserver peer
            # will show an error about us killing the connection
            # prematurely instead of showing the URL that causes the
            # error. Flushing the data here helps.
            if exc_info:
                response = fp.read()
                fp.close()
                # And, even more importantly. Some people want the
                # exception/error info. Store it in our HTTPError
                # subclass.
                raise HTTPError(
                    exc_info[1].url,
                    exc_info[1].code,
                    exc_info[1].msg,
                    exc_info[1].hdrs,
                    response
                )
            fp.close()

    if exc_info:
        raise stored_exception  # exc_info[0], exc_info[1], exc_info[2]
    return response


class HttpTestCase(TestCase):
    class TestServer(object):
        "Supersimple builtin HTTP test server."
        def __init__(self, method, code, body, use_ssl=False):
            from multiprocessing import Process
            from socket import socket

            self.method = method
            self.code = code
            self.body = body

            self.socket = socket()
            if use_ssl:
                here = path.dirname(__file__)
                self.socket = ssl.wrap_socket(
                    self.socket,
                    certfile=path.join(here, 'http-testserver.crt'),
                    keyfile=path.join(here, 'http-testserver.key'))
            self.socket.bind(('127.0.0.1', 0))
            # We must listen() before starting the subprocess, otherwise
            # the main process may get a connection refused if it's too
            # fast.
            self.socket.listen(0)
            self.port = self.socket.getsockname()[1]

            self.process = Process(target=self.respond)
            self.process.start()
            self.socket.close()  # client is done with it

        def join(self):
            self.process.join()

        def respond(self):
            try:
                peersock, peeraddr = self.socket.accept()
            except ssl.SSLError:
                # Broken connection by peer.
                return

            data = peersock.recv(4096)
            if HttpTestCase.to_str(data).startswith(self.method):
                peersock.send(
                    ('HTTP/1.0 %s Whatever\r\n'
                     'Content-Type: text/plain; utf-8\r\n'
                     '\r\n%s' % (self.code, self.body)
                     ).encode('utf-8'))
            else:
                peersock.send(
                    ('HTTP/1.0 999 Unexpected stuff\r\n'
                     'Content-Type: text/plain; utf-8\r\n'
                     '\r\nUnexpected stuff'
                     ).encode('utf-8'))
            peersock.close()
            self.socket.close()  # server is done with it

    def test_options_or_operator(self):
        a = Options()
        a.protocols = ('ftp',)
        a.cacert_file = 'overwrite_me'
        b = Options()
        b.cacert_file = '/tmp/test.crt'
        c = a | b

        self.assertEqual(c.protocols, ('ftp',))
        self.assertFalse(c.verify_cert)
        self.assertEqual(c.cacert_file, '/tmp/test.crt')

    def test_testserver(self):
        "Ensure that the testserver refuses if the method is bad."
        server = HttpTestCase.TestServer('FAIL', '555', 'failure')
        self.assertRaises(HTTPError, http_get,
                          'http://127.0.0.1:%d/path' % (server.port,))
        server.join()

    def test_delete(self):
        server = HttpTestCase.TestServer('DELETE', '200', 'whatever1')
        data = http_delete('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever1')

    def test_get(self):
        server = HttpTestCase.TestServer('GET', '200', 'whatever2')
        data = http_get('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever2')

    def test_post(self):
        server = HttpTestCase.TestServer('POST', '200', 'whatever3')
        data = http_post('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever3')

    @skip('still needed: a test that actually checks the posted data')
    def test_post_actual_data(self):
        self.assertFalse(True)

    def test_put(self):
        server = HttpTestCase.TestServer('PUT', '200', 'whatever4')
        data = http_put('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever4')

    def test_502(self):
        server = HttpTestCase.TestServer('GET', '502', 'eRrOr')
        try:
            http_get('http://127.0.0.1:%d/path' % (server.port,))
        except HTTPError as e:
            self.assertTrue(isinstance(e, request.HTTPError))
            self.assertEqual(e.code, 502)
            self.assertDataEqual(e.response, 'eRrOr')
        else:
            self.assertFalse(True)
        server.join()

    def test_https_only_through_options(self):
        self.assertRaises(BadProtocol, http_get,
                          'http://127.0.0.1/path', opt=opt_secure)
        self.assertRaises(BadProtocol, http_get,
                          'ftp://127.0.0.1/path', opt=opt_secure)

    def test_https_no_secure(self):
        server = HttpTestCase.TestServer('GET', '200', 'ssl', use_ssl=True)
        data = http_get('https://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'ssl')

    def test_https_with_real_secure(self):
        # This should work with a proper certificate.
        data = http_get('https://api.github.com/', opt=opt_secure)
        self.assertEqual(HttpTestCase.to_str(data)[0:1], '{')  # json :)

    def test_https_with_self_signed(self):
        # This should fail, because the testserver uses a self-signed
        # certificate.
        server = HttpTestCase.TestServer('GET', '200', 'ssl', use_ssl=True)
        self.assertRaises(request.URLError, http_get,
                          'https://127.0.0.1:%d/path' % (server.port,),
                          opt=opt_secure)
        server.join()

        # Retry when using that crt in the allow list. It should be
        # allowed this time.
        my_opt = Options()
        my_opt.cacert_file = path.join(
            path.dirname(__file__), 'http-testserver.crt')
        my_opt = opt_secure | my_opt
        server = HttpTestCase.TestServer('GET', '200', 'ssl2', use_ssl=True)
        data = http_get('https://127.0.0.1:%d/path' % (server.port,),
                        opt=my_opt)
        server.join()
        self.assertDataEqual(data, 'ssl2')

    # ; Python23 compatibility helpers

    try:
        unicode  # python2
    except NameError:
        to_str = staticmethod(lambda x: x.decode('utf-8'))  # unistr
    else:
        to_str = staticmethod(lambda x: x)  # binstr

    def assertDataEqual(self, data, unistr):
        """
        Compares http_* returned data with a plain string. That plain string
        can be unicode (python3) or binstring (python2). The data is always a
        binstring.
        """
        unistr_passed = self.to_str(data)
        self.assertEqual(unistr_passed, unistr)


if __name__ == '__main__':
    main()
