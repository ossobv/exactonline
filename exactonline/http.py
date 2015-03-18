# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
HTTP shortcuts, taken from osso-djuty.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.

We may want to replace this with something simpler.
"""
import httplib
import urllib
import urllib2
import urlparse
import socket
import ssl
import sys

from unittest import TestCase, main, skip


# ; helpers

def binquote(value):
    """
    We use quote() instead of urlencode() because the Exact Online API
    does not like it when we encode slashes -- in the redirect_uri -- as
    well (which the latter does).
    """
    return urllib.quote(value.encode('utf-8'))

urljoin = urlparse.urljoin


# ; http stuff

class BadProtocol(ValueError):
    """
    Raised when you try to http_get or http_post with a disallowed
    protocol.
    """
    pass


class HTTPError(urllib2.HTTPError):
    """
    Override the original HTTPError, drop the fp and add a response.
    """
    def __init__(self, url, code, msg, hdrs, response):
        urllib2.HTTPError.__init__(self, url, code, msg, hdrs, None)
        self.response = response

    def __str__(self):
        assert isinstance(self.response, str)
        response = self.response[0:512] + ('', '...')[len(self.response) > 512]
        response = ''.join(('?', i)[0x20 <= ord(i) <= 0x7F or i in '\t\n\r']
                           for i in response)
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


class Request(urllib2.Request):
    """
    Override the urllib2.Request class to supply a custom method.
    """
    def __init__(self, method=None, *args, **kwargs):
        urllib2.Request.__init__(self, *args, **kwargs)
        assert method in ('DELETE', 'GET', 'POST', 'PUT')
        self._method = method

    def get_method(self):
        return self._method


class ValidHTTPSConnection(httplib.HTTPConnection):
    """
    This class allows communication via SSL.

    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    default_port = httplib.HTTPS_PORT
    cacert_file = opt_default.cacert_file

    def __init__(self, *args, **kwargs):
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, ca_certs=self.cacert_file,
                                    cert_reqs=ssl.CERT_REQUIRED)


class ValidHTTPSHandler(urllib2.HTTPSHandler):
    """
    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    def __init__(self, cacert_file):
        self.cacert_file = cacert_file
        urllib2.HTTPSHandler.__init__(self)

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
        data = ''  # ensure POST-mode
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
        data = ''  # ensure POST-mode
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
        opener = urllib2.build_opener(ValidHTTPSHandler(opt.cacert_file))
    else:
        opener = urllib2.build_opener()

    # Create the Request with optional extra headers.
    req = Request(url=url, data=data, method=method,
                  headers=(opt.headers or {}))

    exc_info, fp = None, None
    try:
        fp = opener.open(req)
        # print fp.info()  # (temp, print headers)
        response = fp.read()
    except urllib2.HTTPError as exception:
        fp = exception.fp  # see finally clause
        exc_info = sys.exc_info()
    except Exception:
        exc_info = sys.exc_info()
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
        raise  # exc_info[0], exc_info[1], exc_info[2]
    return response


class HttpTestCase(TestCase):
    class TestServer(object):
        "Supersimple builtin HTTP test server."
        def __init__(self, method, code, body):
            from multiprocessing import Process
            from socket import socket

            self.method = method
            self.code = code
            self.body = body

            self.socket = socket()
            self.socket.bind(('127.0.0.1', 0))
            self.port = self.socket.getsockname()[1]

            self.process = Process(target=self.respond)
            self.process.start()

        def join(self):
            self.socket.close()
            self.process.join()

        def respond(self):
            self.socket.listen(0)
            peersock, peeraddr = self.socket.accept()
            data = peersock.recv(4096)
            if data.startswith(self.method):
                peersock.send(
                    'HTTP/1.0 %s Whatever\r\n'
                    'Content-Type: text/plain; utf-8\r\n'
                    '\r\n%s' % (self.code, self.body))
            else:
                peersock.send(
                    'HTTP/1.0 999 Unexpected stuff\r\n'
                    'Content-Type: text/plain; utf-8\r\n'
                    '\r\nUnexpected stuff')
            peersock.close()

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
        self.assertEqual(data, 'whatever1')

    def test_get(self):
        server = HttpTestCase.TestServer('GET', '200', 'whatever2')
        data = http_get('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertEqual(data, 'whatever2')

    def test_post(self):
        server = HttpTestCase.TestServer('POST', '200', 'whatever3')
        data = http_post('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertEqual(data, 'whatever3')

    def test_put(self):
        server = HttpTestCase.TestServer('PUT', '200', 'whatever4')
        data = http_put('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertEqual(data, 'whatever4')

    def test_502(self):
        server = HttpTestCase.TestServer('GET', '502', 'eRrOr')
        try:
            http_get('http://127.0.0.1:%d/path' % (server.port,))
        except HTTPError as e:
            self.assertTrue(isinstance(e, urllib2.HTTPError))
            self.assertEqual(e.code, 502)
            self.assertIn('eRrOr', e.response)
        else:
            self.assertFalse(True)
        server.join()

    def test_https_only(self):
        self.assertRaises(BadProtocol, http_get,
                          'http://127.0.0.1:80/path', opt=opt_secure)

    @skip('this test is not done yet')
    def test_fixme_fixme(self):
        # - test actual POST data
        # - test secure stuff?

        # Domain with bad cert.
        bad_cert_url = 'https://bad.cert.example.com/'

        # Test that HTTPS does a proper check.
        print('Testing HTTPS http_get')
        http_get('https://example.com/')     # good cert
        http_get(bad_cert_url)               # bad cert, but don't care

        print('Testing HTTPS-secure http_get')
        http_get('https://example.com/', opt=opt_secure)
        try:
            http_get(bad_cert_url, opt=opt_secure)
        except urllib2.URLError:
            pass  # ok!
        else:
            assert False, ('We did not catch the bad certificate of %r' %
                           (bad_cert_url,))


if __name__ == '__main__':
    main()
