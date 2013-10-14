#!/usr/bin/env python
'''test middleware dbi
'''

import os
import sys
import datetime
import unittest

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.middleware.middleware import application
from web3.middleware.session import Cookie, Session, Sqlite, JSON

class TestSqlite(unittest.TestCase):

    def setUp(self):
        self._app = application
        self._env = {'wsgi.multiprocess':False, 'wsgi.multithread':False}
        self._delay = 3600      # sec
        self._sqlite = Sqlite(':memory:', self._delay)

    def tearDown(self):
        del self._sqlite

    def test_get(self):
        self.test_save()

    def test_save(self):
        id_ = 1234
        data = JSON('uid=abcdef')
        self._sqlite.save(id_, data)
        self.assertTrue(self._sqlite.exists(id_), 'first save success')
        raw_data = dict(a=1, b=2)
        data = JSON(raw_data)
        self._sqlite.save(id_, data)
        result = self._sqlite.get(id_)
        # print('---------------')
        # print(repr(result))
        # print(repr(data.obj))
        # print(repr(result[-1].obj))
        # print(type(result[-1]))
        # print('---------------')
        if result:
            self.assertIsInstance(result[-1], JSON, 'return datatype ok')
            self.assertDictEqual(raw_data, result[-1].obj, 'update data success')
        
    def test_delete(self):
        id_ = 2234
        data = 'uid=abcdef'
        self._sqlite.save(id_, data = data)
        exists = self._sqlite.exists(id_)
        self.assertTrue(exists, 'save success')
        if exists:
            self._sqlite.delete(id_)
            exists = self._sqlite.exists(id_)
            self.assertFalse(exists, 'delete success')

    def test_not_delay(self):
        id_ = 3234
        data = 'uid=abcdef'
        self._sqlite.save(id_, data = data)
        exists = self._sqlite.exists(id_)
        self.assertTrue(exists, 'first save success')
        # result = self._sqlite.get(id_)
        # print('update before:', result)
        if exists:
            sql = "UPDATE _sessions SET expires = datetime(expires, '-{} seconds') WHERE id=?".format(self._delay)
            result = self._sqlite.handler.execute(sql, (id_,)).rowcount
            if result:
                # result = self._sqlite.get(id_)
                # print('update after:', result)
                delay = self._sqlite.delay(id_)
                # print('---', repr(delay), '---')
                # result = self._sqlite.get(id_)
                # print('delay after:', result)
                self.assertFalse(delay, 'not delay pass 1')
                exists = self._sqlite.exists(id_)
                self.assertFalse(exists, 'not delay pass 2')

    def test_delay(self):
        id_ = 4234
        raw_data = 'uid=abcdef'
        data = JSON(raw_data)
        self._sqlite.save(id_, data)
        exists = self._sqlite.exists(id_)
        self.assertTrue(exists, 'first save success')

        result = self._sqlite.get(id_)
        # print('update before:', result)
        dt0 = result[1]
        if exists:
            delay = self._delay/2
            sql = "UPDATE _sessions SET expires = datetime(expires, '-{} seconds') WHERE id=?".format(delay)
            result = self._sqlite.handler.execute(sql, (id_,)).rowcount
            if result:
                result = self._sqlite.get(id_)
                # print('update after:', result)
                dt1 = result[1]
                result = self._sqlite.delay(id_)
                # print('---', repr(delay), '---')
                result = self._sqlite.get(id_)
                # print('delay after:', result)
                dt2 = result[1]
                self.assertEqual(dt0, dt2, 'delay pass1')
                # fmt = '%Y-%m-%d %H:%M:%S'
                # print(repr(dt2))
                # print(repr(dt1))
                # td = datetime.datetime.strptime(dt2, fmt) - datetime.datetime.strptime(dt1, fmt)
                td = dt2 - dt1
                self.assertEqual(td.seconds, delay, 'delay pass2')
                
        

class TestSession(unittest.TestCase):

    def setUp(self):
        self._app = application
        self._env = {'wsgi.multiprocess':False, 'wsgi.multithread':False}
        self._delay = 3600      # sec
        self._sqlite = Sqlite(':memory:', self._delay)
        self._session()

    def tearDown(self):
        if self._sqlite:
            del self._sqlite

    def _session(self):
        id_ = '123454321'
        data = JSON('uid=1234')
        self._sqlite.save(id_, data)

    def testSessionRegister(self):
        def app(environ):
            session = environ.get('wsgi.session', None)
            if session:
                self.assertIs(session.get('id', None), None, 'session id exists')
                self.assertEqual(session.get('name', None), 'sid', 'session name exists')

                data = 'mydata'
                sid, sdata = Session.register(environ, data)
                # print(repr(sid), repr(sdata))
                if sid:
                    storage = session['storage']
                    row = storage.get(sid)
                    self.assertEqual(row[-1].obj, data, 'register session data match')
                    qs = environ.get('QUERY_STRING', None)
                    self.assertTrue(qs, 'register url session')
                    if qs:
                        self.assertRegex(qs, '='.join(('sid', str(sid))), 'register url session id match')
                    if 'wsgi.setcookie' in environ:
                        sid_cookie = environ['wsgi.setcookie'].get('sid', None)
                        self.assertTrue(sid_cookie, 'register cookie session')
                        if sid_cookie:
                            self.assertEqual(sid, sid_cookie.value, 'register cookie session id match')
            return '200 ok', [], []

        app = Cookie(app)
        app = Session(app, self._sqlite)
        status, headers, body = app(self._env)
        found_setcookie = [True for h, v  in headers if  v.startswith('sid=')]
        self.assertTrue(found_setcookie, 'register cookie session header output success')

    def testSession(self):
        def app(environ):
            rdata = JSON('uid=1234')
            session = environ.get('wsgi.session', None)
            if session:
                id_ = session['id']
                storage = session['storage']
                sdata = session['data']
                cols = storage.get(id_)
                #print(repr(row))
                self.assertIn(id_, cols, 'session exists')
                self.assertEqual(rdata.obj, sdata.obj, 'session store data match')
                self.assertEqual(rdata.obj, cols[-1].obj, 'session store data match')

            return '200 OK', [], []

        env = self._env.copy()
        env['HTTP_COOKIE']='count=1; Path=/\r\n sid=123454321; Path=/private'

        app = Cookie(app)
        app = Session(app, self._sqlite)
        status, headers, body = app(env)


    def testSessionExpires(self):
        def app(environ):
            session = environ.get('wsgi.session', None)
            if session:
                id_ = session['id']
                self.assertFalse(id_, 'not delay session')

                Session.unregister(environ, id_)
                cookie = environ.get('wsgi.cookie', None)
                if cookie:
                    sid_cookie = cookie['sid']
                    self.assertTrue(sid_cookie, 'not delay session cookie input')
                    sid = sid_cookie.value
                    self.assertEqual(sid, '1234567890', 'not delay sessionid match')

                if 'wsgi.setcookie' in environ:
                    sid_setcookie = environ['wsgi.setcookie'].get('sid', None)
                    self.assertTrue(sid_setcookie, 'not delay session cookie expires')

            return '200 ok', [], []

        env = self._env.copy()
        env['HTTP_COOKIE']='count=1; Path=/\r\n sid=1234567890; Path=/private'

        app = Cookie(app)
        app = Session(app, self._sqlite)
        status, headers, body = app(env)
        found_setcookie = [True for h, v  in headers if  v.startswith('sid=')]
        self.assertTrue(found_setcookie, 'register cookie session header output success')



class TestCookie(unittest.TestCase):

    def setUp(self):
        self._app = application
        self._env = {'wsgi.multiprocess':False, 'wsgi.multithread':False}

    def tearDown(self):
        pass


    def testCookie(self):
        def app(environ):
            cookie = environ['wsgi.cookie']
            count_cookie = cookie['count']
            self.assertEqual('1', count_cookie.value, 'read cookie:count')

            sid_cookie = cookie['sid']
            self.assertEqual('1234567890', sid_cookie.value, 'read cookie:sid')
            self.assertEqual('/private', sid_cookie['path'], 'read cookie:sid.path')

            return '200 ok', [], []

        env = self._env.copy()
        env['HTTP_COOKIE']='count=1; Path=/\r\n sid=1234567890; Path=/private'
        app = Cookie(app)
        status, headers, body = app(env)


    def testSetCookie(self):
        def app(environ):
            environ['wsgi.setcookie']['count'] = 1
            environ['wsgi.setcookie']['count']['path'] = '/'
            environ['wsgi.setcookie']['sid'] = 1234567890
            environ['wsgi.setcookie']['sid']['path'] = '/private'

            return '200 ok', [('Content-Type','text/plain')], []

        app = Cookie(app)
        response = app(self._env)
        if response:
            status, headers, body = response
            #print(headers)
            for k, v in headers:
                if 'Cookie' in k:
                    if 'count' in v:
                        self.assertRegex(v, 'count=1', 'set-cookie: count=1')
                    if 'sid' in v:
                        self.assertRegex(v, 'sid=1234567890', 'set-cookie: sid=1234567890')
                        self.assertRegex(v, 'Path=/private', 'set-cookie: sid=1234567890; Path=/Private')


def suite():
    suite = unittest.TestSuite()

    suite.addTest(TestCookie)
    suite.addTest(TestSqlite)
    suite.addTest(TestSession)

    return suite

if '__main__' == __name__:
    unittest.main()
