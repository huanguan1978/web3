#!/usr/bin/env python
'''test server
'''

import os
import sys
import re
import unittest
sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.middleware.middleware import application
from web3.middleware.route import Route
from web3.lib.node import Node
from web3.lib.helper import Helper

# test nods

class Base(Node, Helper):

    def get(self, env):
        body = b'base page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]

class Private(Node, Helper):

    def get(self, env):
        body = b'private page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]

class Verification(Node, Helper):

    def get(self, env):
        body = b'verification page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]

class MemberInfo(Node, Helper):

    def get(self, env):
        body = 'member-info page'
        status = '200 ok'
        headers = [('Content-Type', 'text/plain')]
        return status, headers, [body]
    
class Demo(Node, Helper):

    def get(self, env):
        body = b'demo page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]




class TestRoute(unittest.TestCase):

    def setUp(self):
        self._app = application
        self._env = {'wsgi.url_scheme':'http', 'HTTP_HOST':'example.com','REQUEST_METHOD':'get', 'PATH_INFO':'/'}
        self._urls = [
            (0, re.compile('.*'), re.compile('^/member-info'), MemberInfo, dict()),
            (0, re.compile('.*'), re.compile('^/private'), Private, dict(get=())),
            (1, re.compile('.*'), re.compile('^/verification'), Verification, dict(get=())),
            (0, re.compile('^demo'), re.compile('^/'), Demo, dict()),
            ]

    def tearDown(self):
        pass


    def test_not_found(self):
        def app(environ):
            return '404 not found', [],[]

        app = Route(app, self._urls)
        env = self._env.copy()
        env['PATH_INFO'] = '/not exists.html'
        status, headers, bodys = app(env)
        
        self.assertEqual(status[:3], '404', '404 not found')


    def test_subdomain(self):
        app = Route(self._app, self._urls)
        env = self._env.copy()
        env['HTTP_HOST'] = 'demo.example.com'
        env['PATH_INFO'] = '/demo'
        status, headers, bodys = app(env)

        r =Demo(env)
        r_status, r_headers, r_bodys = r.get(env)

        self.assertEqual(status, r_status, 'success response status')
        self.assertListEqual(headers, r_headers, 'success response body')
        self.assertListEqual(bodys, r_bodys, 'success response body')

    def test_authc(self):
        app = Route(self._app, self._urls)
        env = self._env.copy()
        env['PATH_INFO'] = '/private'
        env['REMOTE_USER'] = 'your_id'
        status, headers, bodys = app(env)

        r =Private(env)
        r_status, r_headers, r_bodys = r.get(env)

        self.assertEqual(status, r_status, 'success response status')
        self.assertListEqual(headers, r_headers, 'success response body')
        self.assertListEqual(bodys, r_bodys, 'success response body')


    def test_authc_tls(self):
        app = Route(self._app, self._urls)
        env = self._env.copy()
        env['wsgi.url_scheme']='https'
        env['PATH_INFO'] = '/verification'
        env['REMOTE_USER'] = 'your_id'
        status, headers, bodys = app(env)

        r =Verification(env)
        r_status, r_headers, r_bodys = r.get(env)

        self.assertEqual(status, r_status, 'success response status')
        self.assertListEqual(headers, r_headers, 'success response body')
        self.assertListEqual(bodys, r_bodys, 'success response body')
        

    def test_path_seo(self):
        app = Route(self._app, self._urls)
        env = self._env.copy()
        env['PATH_INFO'] = '/member-info/1234'
        status, headers, bodys = app(env)

        r = MemberInfo(env)
        r_status, r_headers, r_bodys = r.get(env)

        self.assertEqual(status, r_status, 'success response status')
        self.assertListEqual(headers, r_headers, 'success response body')
        self.assertListEqual(bodys, r_bodys, 'success response body')
        
            
if '__main__' == __name__:
    unittest.main()


