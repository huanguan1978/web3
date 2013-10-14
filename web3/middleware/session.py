#!/usr/bin/env python
''' web3 middleware session
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '10 Jan 2012'
__credits__ = 'no credits'

import abc
import time
import random
import sqlite3

from http import cookies
from json import dumps, loads
from urllib.parse import parse_qs

from .middleware import Middleware, SideBySide

## dbapi2 datatype json support, begin....
class JSON:
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return "{}.{}({})".format(self.__module__, self.__class__.__name__, repr(self.obj))

def adapt_point(instance):
    return dumps(instance.obj)

def convert_point(text):
    return JSON(loads(text.decode()))

# Register the adapter
#sqlite3.register_adapter(JSON, adapt_point)

# Register the converter
#sqlite3.register_converter('json', convert_point)

#p = JSON(dict(a=1,b=2))
## dbapi2 datatype json support, end....

class Storage(metaclass = abc.ABCMeta):
    
    def __init__(self, database:str=':memory:', expires:int=3600):
        self.__database = database
        self.__expires = expires
        self.__handler = None

    def __del__(self):
        if self.handler:
            if hasattr(self.handler, 'commit'):
                self.handler.commit()
            if hasattr(self.handler, 'close'):
                self.handler.close()

    @abc.abstractproperty
    def database(self):
        return self.__database

    @abc.abstractproperty
    def expires(self):
        return self.__expires
    @expires.setter
    def expires(self, expires):
        self.__expires = expires
        return self.__expires

    @abc.abstractproperty
    def handler(self) ->object:
        if self.__handler:
            return self.__handler
        try:
            sqlite3.register_adapter(JSON, adapt_point)
            sqlite3.register_converter('json', convert_point)
            self.__handler = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
            self.__handler.isolation_level = None # autocommit
            # self.__handler.row_factory = sqlite3.Row
        except:
            if hasattr(self.__handler, 'close'):
                self.__handler.close()
        else:
            try:
                self.prepare(self.__handler)
            except:
                raise
            
        return self.__handler

    @handler.setter
    def handler(self, handler:object) -> object:
        self.__handler = handler
        try:
            self.prepare(self.__handler)
        except:
            raise
        return self.__handler

    @abc.abstractmethod
    def prepare(self, handler:object):
        sql = 'CREATE TABLE IF NOT EXISTS _sessions (id TEXT NOT NULL PRIMARY KEY, expires TIMESTAMP NOT NULL, data JSON);'
        cursor = None
        try:
            cursor = handler.cursor()
        except:
            raise
        else:
            cursor.execute(sql)
        finally:
            if hasattr(cursor, 'close'):
                cursor.close()

    @abc.abstractmethod
    def exists(self, id_:str) -> bool:
        sql = 'SELECT 1 FROM _sessions WHERE id=?'

        cursor = self.handler.cursor()
        cursor.execute(sql, (id_, ))
        fetchone = cursor.fetchone()
        cursor.close()

        return fetchone


    @abc.abstractmethod
    def get(self, id_:str) -> tuple:
        sql = 'SELECT * FROM _sessions WHERE id=?'

        cursor = self.handler.cursor()
        cursor.execute(sql, (id_,))
        fetchone = cursor.fetchone()
        cursor.close()

        return fetchone

    @abc.abstractmethod
    def delete(self, id_:str) -> int:
        sql = 'DELETE FROM _sessions WHERE id=?'

        cursor = self.handler.cursor()
        cursor.execute(sql, (id_, ))
        cursor.close()

        return cursor.rowcount

    @abc.abstractmethod        
    def save(self, id_:str, data:str) -> int:
        if self.exists(id_):
            sql = 'UPDATE _sessions SET data=? WHERE id=?'
            params = (data, id_)
        else:
            sql = "INSERT INTO _sessions(expires, data, id) VALUES(datetime('now', '{} seconds'), ?, ?)".format(self.expires)
            params = (data, id_)

        return self.handler.execute(sql, params).rowcount

    @abc.abstractmethod
    def delay(self, id_:str) -> tuple:
        sql = "DELETE FROM _sessions WHERE strftime('%s', expires) <= strftime('%s', 'now')"
        self.handler.execute(sql)

        sql = "UPDATE _sessions SET expires =  datetime( strftime('%s', expires) + ({} - (strftime('%s', expires) - strftime('%s', 'now'))) , 'unixepoch') WHERE id=? AND ( (strftime('%s',expires) - strftime('%s', 'now')) <= {} )".format(self.expires, self.expires)

        return self.handler.execute(sql, (id_,)).rowcount


class Sqlite(Storage):

    def __init__(self, database:str=':memory:', expires:int=3600):
        self.__database = database
        self.__expires = expires
        self.__handler = None

        super().__init__(database, expires)

    def __del__(self):
        super().__del__()

    @property
    def database(self):
        return super().database

    @property
    def expires(self):
        return super().expires
    @expires.setter
    def expires(self, expires):
        return super().expires(expires)

    @property
    def handler(self):
        return super().handler
    @handler.setter
    def handler(self, handler):
        handler.isolation_level = None # autocommit
        return super().handler(handler)

    def prepare(self, handler:object):
        return super().prepare(handler)

    def exists(self, id_:str) ->bool:
        return super().exists(id_)

    def get(self, id_:str) ->tuple:
        return super().get(id_)

    def delete(self, id_:str) -> int:
        return super().delete(id_)

    def save(self, id_:str, data:str) -> int:
        return super().save(id_, data)

    def delay(self, id_:str) -> int:
        return super().delay(id_)


class Psycopg2(Storage):

    def __init__(self, database:str=':memory:', expires:int=3600):
        self.__database = database
        self.__expires = expires
        self.__handler = None
        super().__init__(database, expires)

    def __del__(self):
        super().__del__()

    @property
    def database(self):
        return self.__database

    @property
    def expires(self):
        return self.__expiress
    @expires.setter
    def expires(self, expires):
        self.__expires = expires
        return self.__expires

    @property
    def handler(self):
        if self.__handler:
            return self.__handler

        try:
            import Psycopg2
            self.__handler = Psycopg2.connect(self.database)
        except:
            raise
        else:
            try:
                self.prepare(self.__handler)
            except:
                raise
        finally:
            if hasattr(self.__handler, 'close'):
                self.__handler.close()
        
        return self.__handler

    @handler.setter
    def handler(self, handler:object) -> object:
        handler.autocommit = True
        return super().handler(handler)

    @abc.abstractmethod
    def prepare(self, handler:object):
        sql = 'CREATE TABLE IF NOT EXISTS _sessions (id TEXT NOT NULL PRIMARY KEY, expires TIMESTAMP NOT NULL, data TEXT);'
        cursor = None
        try:
            cursor = handler.cursor()
        except:
            raise
        else:
            cursor.execute(sql)
        finally:
            if hasattr(cursor, 'close'):
                cursor.close()


    def exists(self, id_:str) -> bool:
        return super().exists(id_)

    def get(self, id_:str) ->tuple:
        return super().get(id_)

    def delete(self, id_:str) -> int:
        return super().delete(id_)
        
    def save(self, id_:str, data:str) -> int:
        if self.exists(id_):
            sql = 'UPDATE _sessions SET data=? WHERE id=?'
            params = (data, id_)
        else:
            sql = "INSERT INTO _sessions(expires, data, id) VALUES((now() + INTERVAL '{} seconds'), ?, ?)".format(self.expires)
            params = (data, id_)

        cursor = self.handler.cursor()
        cursor.execute(sql, params)
        cursor.close()

        return cursor.rowcount

    def delay(self, id_:str) -> int:
        cursor = self.handler.cursor()

        sql = "DELETE FROM _sessions WHERE expires <= now()"
        cursor.execute(sql)

        sql = "UPDATE _sessions SET expires = expires + ({} - extract('epoch' from (expires - now()))) WHERE =? AND ({} - extract('epoch' from (expires - now()))) <={}".format(self.expires, self.expires)
        cursor.execute(sql, (id_, ))

        cursor.close()

        return cursor.rowcount
        

class Cookie(SideBySide):

    def __init__(self, app:object):
        self._app = app

    def __call__(self, environ):

        
        def func(status, headers, body):
            return status, headers, body

        def helper(app, environ, func):

            http_cookie = environ.get('HTTP_COOKIE', None)
            cookie = cookies.SimpleCookie(http_cookie)
            environ['wsgi.cookie'] = cookie
            if 'wsgi.setcookie' not in environ:
                environ['wsgi.setcookie'] = cookies.SimpleCookie()

            if environ.get('wsgi.debug', None):
                msg = "cookie:{}".format(repr(cookie))
                print(self._msg(msg), file=environ['wsgi.errors'])

            app_response = app(environ)
            if not hasattr(app_response, '__call__'):
                setcookie = environ.get('wsgi.setcookie', None)
                if setcookie:
                    cookie_headers = [header.split(': ') for header in setcookie.output().split('\r\n') ]
                    status, headers, body = app_response
                    headers.extend([tuple(h) for h in cookie_headers])
                    if environ.get('wsgi.debug', None):
                        msg = "setcookie{}".format(repr(setcookie))
                        print(self._msg(msg), file=environ['wsgi.errors'])

                    return func(status, headers, body)
                return func(*app_response)

            raise Exception

        def sidebyside(app):
            def wrapper(envrion):
                return helper(app, environ, func)
            return wrapper

        return sidebyside(self._app)(environ)



class Session(Middleware):
    def __init__(self, app:object, storage:object, name:str='sid'):
        self._app  = app
        self._name = name
        self._storage = storage

    def __del__(self):
        del self._storage

    def __call__(self, environ):
        id_ = None

        cookie = environ.get('wsgi.cookie', None)
        if not cookie:            
            http_cookie = environ.get('HTTP_COOKIE', None)
            if http_cookie:
                cookie = cookies.SimpleCookie(http_cookie)

        if cookie:
            id_cookie = cookie.get(self._name, None)
            if id_cookie:
                id_ = id_cookie.value

        if not id_:
            qs = environ.get('QUERY_STRING', None)
            if qs:
                qs = parse_qs(qs)
                id_ = qs.get(self._name, None)

        environ['wsgi.session_register'] = self.register
        environ['wsgi.session_unregister'] = self.unregister
        environ['wsgi.session'] = dict(
            id = id_,
            data = None,
            name = self._name,
            storage = self._storage
            )

        if id_:
            if not self._storage.delay(id_):
                self.unregister(environ, False)
                environ['wsgi.session']['id'] = None
            else:
                row = self._storage.get(id_)
                if row:
                    data = row[-1]
                    if data:
                        environ['wsgi.session']['data'] = data
                        if isinstance(data, JSON):
                            if 'REMOTE_USER' in data.obj:
                                environ['REMOTE_USER'] = data.obj['REMOTE_USER']
                            if 'REMOTE_ROLE' in data.obj:
                                environ['REMOTE_ROLE'] = data.obj['REMOTE_ROLE']
                    

        if environ.get('wsgi.debug', None):
            msg = "name:{},id:{}".format(
                    self._name, repr(id_)
                    )
            print(self._msg(msg), file=environ['wsgi.errors'])

        return self._app(environ)


    @staticmethod
    def register(environ:dict, data, option:dict=dict()) ->tuple:
        '''register session data, return (sessionid, data) '''
        session = environ.get('wsgi.session', None)
        id_, data_, name, storage = session['id'], session['data'], session['name'], session['storage']

        if id_:
            if data_:
                data_.update(data)
            if data:
                if data_:
                    data_.update(data)
                    data = data_
                storage.save(id_, JSON(data))
            return (id_, data)

        random.seed(time.time())
        id_ = str(random.random())

        if data:
            storage.save(id_, JSON(data))

        #session cookie
        if 'wsgi.setcookie' in environ:
            environ['wsgi.setcookie'][name] = id_

            cookie = environ.get('wsgi.cookie', None)
            if cookie and cookie.get(name, None):
                for k, v in cookie[name].items():
                    if v:
                        environ['wsgi.setcookie'][name][k] = v

            if option and isinstance(option, dict):
                environ['wsgi.setcookie'][name].update(option)

        # session url eg: http://you.domain/?arg1=1234&sessionid=1234
        qs = environ.get('QUERY_STRING', None)
        if qs:
            name += '='
            if name not in qs:
                name += id_
                environ['QUERY_STRING'] = '&'.join((name, qs))
        else:
            environ['QUERY_STRING'] = '='.join((name, id_))

        return (id_, data)

    @staticmethod    
    def unregister(environ, exists:bool=True):
        session = environ.get('wsgi.session', None)
        if session:
            id_, name, storage = session['id'], session['name'], session['storage']
            if id_ and exists:
                storage.delete(id_)

            cookie = environ.get('wsgi.cookie', None)
            if cookie and cookie.get(name, None):
                cookie[name]['max-age'] =0
                cookie[name]['expires'] = -3600

                if not isinstance(environ['wsgi.setcookie'].get(name, None), cookies.SimpleCookie):
                    environ['wsgi.setcookie'] = cookies.SimpleCookie()
                    environ['wsgi.setcookie'][name] = cookie[name].value

                for k, v in cookie[name].items():
                    if v:
                        environ['wsgi.setcookie'][name][k] = v

            qs = environ.get('QUERY_STRING', None)
            if qs:
                name = '='.join((name, id_)) if id_ else '='.join((name,))
                if name in qs:
                    environ['QUERY_STRING'] = qs.replace(name, '').strip('&')
