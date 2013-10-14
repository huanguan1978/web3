#!/usr/bin/env python
'''test middleware dbi
'''

import os
import sys
import zlib
import unittest

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.middleware.middleware import application
from web3.middleware.zip import Zip

class TestZip(unittest.TestCase):
    
    def setUp(self):
        self._app = application
        self._env = {'wsgi.multiprocess':False, 'wsgi.multithread':False}
        self._body = 'abcdefg1234567890' * 32768

    def tearDown(self):
        pass

    def test_gzip(self):
        def app(environ):
            body = self._body
            return '200 OK', [], [body]
            
        env = self._env.copy()
        env['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate'
        env['REQUEST_METHOD'] = 'GET'
        env['wsgi.url_scheme'] = 'http'

        app = Zip(app)
        status, headers, body = app(env)
        # body = body[0]
        # self.assertEqual(self._body.encode(), zlib.decompress(body.encode()), 'data match')

        for h, v in headers:
            h = h.lower()
            v = v.lower()
            
            if h == 'content-length':
                self.assertTrue(h, 'content-length header exists')
                self.assertLess(int(v), len(self._body), 'size less not gzip')
                continue

            if h == 'content-type':
                self.assertTrue(h, 'content-type header exists')
                self.assertIn('gzip', v, 'content-type gzip')
                continue
            
            if h == 'vary':
                self.assertTrue(h, 'vary header exists')
                self.assertIn('accept-encoding', v, 'vary accept-encoding')
                self.assertIn('content-encoding', v, 'vary content-encoding')
                continue

if '__main__' == __name__:
    unittest.main()
