#!/usr/bin/env python

import os
import sys
import unittest
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.middleware.middleware import application
from web3.middleware.auth import AuthDigest

def get_password(environ):
    pass

class AuthDigestTestCase(unittest.TestCase):

    def setUp(self):
        self._env = {'wsgi.url_scheme':b'http', 'REQUEST_METHOD':b'GET', 'PATH_INFO':b'/dir/index.html',
                        'HTTP_AUTHORIZATION':b'Digest username="Mufasa",realm="testrealm@host.com",nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",uri="/dir/index.html",qop=auth,nc=00000001,cnonce="0a4f113b",response="6629fae49393a05397450978507c4ef1",opaque="5ccc069c403ebaf9f0171e9517f40e41"'}
        self._username = 'Mufasa'
        self._realm = 'testrealm@host.com'
        self._password = 'Circle Of Life'
        self._auth_path = '/dir/index.html'
        self._auth_domain = '/dir'
        self._app_iter = AuthDigest(application, get_password, self._auth_path, self._auth_domain, self._realm)

    def tearDown(self):
        pass

    def test_HA1(self):
        HA1 = '939e7578ed9e3c518a452acee763bce9'
        a1 = self._app_iter.a1(self._username, self._realm, self._password)
        ha1 = self._app_iter.h(a1)
        self.assertEqual(HA1, ha1)

        HA1 = '4f1038ca86d403c0d3ba5c87327414fc'
        a1 = self._app_iter.a1('9223372036854775807', 'localhost', '987654321')
        ha1 = self._app_iter.h(a1)
        self.assertEqual(HA1, ha1)


    def test_HA2(self):
        HA2 = '39aff3a2bab6126f332b942af96d3366'
        a2 = self._app_iter.a2(self._env['REQUEST_METHOD'].decode(), self._env['PATH_INFO'].decode())
        ha2 = self._app_iter.h(a2)
        self.assertEqual(HA2, ha2)

    def test_response(self):
        response = '6629fae49393a05397450978507c4ef1'
        auth_header = self._env['HTTP_AUTHORIZATION'].decode()
        auth_header_dict = self._app_iter.digest2dict(auth_header)
        
        a1 = self._app_iter.a1(self._username, self._realm, self._password)
        a2 = self._app_iter.a2(self._env['REQUEST_METHOD'].decode(), self._env['PATH_INFO'].decode())
        nonce = self._app_iter.nonce(auth_header_dict)
        digest = self._app_iter.digest(a1, nonce, a2)
        
        self.assertEqual(response, digest)
        

if __name__ == '__main__':
    unittest.main()
