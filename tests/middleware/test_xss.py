#!/usr/bin/env python
'''test server
'''
import re
import os
import sys
import unittest
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.middleware.middleware import application
from web3.middleware.xss import XSS


class TestXSS(unittest.TestCase):

    def setUp(self):
        self._app = application
        self._env = {'wsgi.url_scheme':'http', 'HTTP_HOST':'localhost','REQUEST_METHOD':'get', 'PATH_INFO':'/'}

    def tearDown(self):
        pass

    def test_qs_js(self):
        '''test query string include script'''
        s = [
            (410, '><script>alert(document.cookie)</script>')
            ,(410, '><script>alert(document.cookie)</script>')
            ,(410, "='><script>alert(document.cookie)</script>")
            ,(410, '"><script>alert(document.cookie)</script>')
            ,(410, '<script>alert(document.cookie)</script>')
            ,(410, '<script>alert(vulnerable)</script>')
            ,(410, "%3Cscript%3Ealert('XSS')%3C/script%3E")
            ,(410, "<script>alert('XSS')</script>")
            ,(410, ''' <img src="javascript:alert('XSS')"> ''')
            ,(410, ''' <img src="http://xxx.com/yyy.png" onerror="alert('XSS')"> ''')
            ,(410, ''' <div style="height:expression(alert('XSS'),1)" />(IE ONLY) ''')
            ]

        env = self._env.copy()
        for code, qs in s:
            env['QUERY_STRING'] = ('q=' + qs)
            status, headers, body  = XSS(self._app)(env)
            self.assertEqual(int(status[0:3]), code, qs)

if '__main__' == __name__:
    unittest.main()
'''
10202
487434GU
liu
23
e
10w
30

--2022
'''
