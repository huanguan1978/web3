#!/usr/bin/env python
'''
wsgi middleware database(dbapi2)

DSN -- The Data Source Name
example:
driver://[username[:password]@host[:port]]/database?options

eg:
MySQLdb://myname:mypassword@localhost:3306/mydb?unix_socket='/tmp/mysql.sock&connect_timeout=60'
pg8000.dbapi://myname:mypassword@localhost:5432/mydb?unix_sock='/tmp/.s.PGSQL.5432'
#py-postgresql
postgresql://myname:mypassword@127.0.0.1:6543/crown?sslmode=require'
postgresql://myname:mypassword@[unix::tmp:.s.PGSQL.5432]/crown?sslmode=require'
#https://github.com/jwp/py-postgresql/issues/53
#psycopg2
psycopg2://myname:mypassword@127.0.0.1:6543/crown?sslmode=require
#psycopg2 unix socketsupport eg: host =/tmp or host=/tmp/.s.PGSQL.5432
psycopg2://myname:mypassword@/tmp/crown?sslmode=require
sqlite3:///:memory:
sqlite3:////tmp/temp.sqlite3
sqlite3://////C:\\path\\to\\database.db

eg:
hub = {}
hub['master'] = 'sqlite3:////temp/temp.sqlite3'
hub['secondary'] = 'postgresql://postgres@127.0.0.1?sslmode=require'

prepare = {}
prepare['secondary'] = '/home/crown/sql/conn_init.sql'
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '25 DEC 2011'
__credits__ = 'no credits'

import re
import warnings

from os.path import exists as  os_path_exists
from os import access as os_access, R_OK as os_R_OK

from .middleware import Middleware

class DB(Middleware):

    def __init__(self, app:object, hub:dict, callback:object=None, prepare:dict=dict()):
        self._re_dsn = re.compile('(\w+)://(.*)/(.*)')
        self._app = app
        self._hub = hub
        self._callback = callback
        self._prepare = prepare
        self._open()

    def __del__(self):
        [v.commit() for v in self._hub.values() if hasattr(v, 'commit')]
        [v.close() for v in self._hub.values() if hasattr(v, 'close')]
        del self._hub

    def __call__(self, environ):
        if not environ.get('wsgi.database', None):

            # if environ['wsgi.multiprocess']:
            #     self._clone()

            # if environ['wsgi.multithread']:
            #     self._clone()

            environ['wsgi.database'] = self._hub

        if environ.get('wsgi.debug', None):
            msg = "activate links:{}".format(','.join(self._hub.keys()))
            print(self._msg(msg), file=environ['wsgi.errors'])

        return self._app(environ)


    def _clone(self):
        for k, connect in self._hub.items():
            self._hub[k] = connect.clone()

    def _open(self):
        for k, dsn in self._hub.items():
            v = self._kwargs(dsn)
            if not v[0]:
                continue

            try:
                driver = __import__(v[0])
            except ImportError as e:
                warnings.warn(repr(e))
            else:
                try:
                    if 'sqlite3' == v[0]:
                        connect = driver.connect(dsn[11:]) #substr sqlite3:///
                    elif 'postgresql' == v[0]:
                        connect = driver.open(dsn.replace('postgresql', 'pq')) #py-postgresql open
                    elif 'psycopg2' == v[0]:
                        connect = driver.connect(' '.join([ '='.join(l) for l in v[1].items()]))
                    else:
                        connect = driver.connect(v[1])

                except driver.OperationalError as e:
                    warnings.warn(repr(e))
                else:
                    if self._callback:
                        self._callback(connect)

                    self._hub[k] = connect
                    if self._prepare:
                        file_ = self._prepare.get(k, None)
                        if file_:
                            if os_path_exists(file_) and os_access(file_, os_R_OK):
                                try:
                                    f = open(file_, 'r')
                                except IOError as e:
                                    warnings.warn(repr(e))
                                else:
                                    sqls = f.read().split(';')
                                    try:
                                        cursor = connect.cursor()
                                    except driver.Error as e:
                                        warnings.warn(repr(e))
                                    else:
                                        for sql in sqls:
                                            try:
                                                connect.execute(sql)
                                            except driver.Error as e:
                                                warnings.warn(repr(e))
                                    finally:
                                        cursor.close()
                                finally:
                                    f.close()



    def _kwargs(self, dsn:str)->tuple:
        # build connection args
        dbtype = dbspec = dbname = dbargs = None
        user = password = host = port = None
        m = self._re_dsn.match(dsn)
        if m:
            dbtype, dbspec, dbname = m.groups()
            if '?' in dbname:
                dbname, dbargs = dbname.split('?')

        if dbtype == 'sqlite3':
            return dbtype, dict()
        if dbtype == 'postgresql':
            return dbtype, dict()

        if dbspec:
            user, password, host, port = self._prase_user_password_host_port(dbspec)

        kwargs = dict()
        if user:
            kwargs['user'] = user
        if password:
            kwargs['password'] = password
        if host:
            kwargs['host'] = host
        if port:
            kwargs['port'] = port
        if dbname:
            kwargs['database'] = dbname
        if dbargs:
            dbargs = dict(map(lambda x:x.split('='), dbargs.split('&')))
            kwargs.update(dbargs)

        if dbtype:
            if 'MySQLdb' == dbtype:
                if password:
                    kwargs['passwd'] = password
                    kwargs.pop('password')
                if dbname:
                    kwargs['db'] = dbname
                    kwargs.pop('database')
            if 'psycopg2' == dbtype:
                if dbname:
                    kwargs['dbname'] = dbname
                    kwargs.pop('database')
        
        return dbtype, kwargs

                    

    def _prase_user_password_host_port(self, user_password_host_port:str)->tuple:
        # arg:str = 'username:password@hostname:port' -> (username, password, hostname, port)
        # arg:str = 'hostname' ->(None, None, hostname, None)
        # arg:str = 'hostname:3306' -> (None, None, hostname, 3306)
        # arg:str = 'username:password@' ->(username, password, None, None)
        # arg:str = 'username@' ->(username, None, None, None)
        # arg:str = 'username@hostname' ->(username, None, hostname, None)
        # arg:str = 'postgres@/tmp'
        # arg:str = 'poweruser@[unix::tmp:.s.PGSQL.5432]' ->(username, None, hostname, None)
        s = user_password_host_port
        user = password = host = port = None
        if '@' in s:
            user_password, host_port = s.split('@')
            if ':' in user_password:
                user, password = user_password.split(':')   # 'user:'.split(':') ->['user', '']
                if not user: user=None
                if not password: password=None
            else:
                user = user_password
            
            if host_port.startswith('[') and host_post.endswith(']'): #pq://poweruser@[unix::tmp:.s.PGSQL.5432]/crown
                host = host_port
            elif ':' in host_port:
                host, port = host_port.split(':')
                if not host: host = None
                if not port: port = None
            else:
                host = host_port
            
        else:
            if s.startswith('[') and s.endswith(']'): # eg:pq://poweruser@[unix::tmp:.s.PGSQL.5432]/crown
                host = host_port
            elif ':' in s:
                host, port = s.split(':')
                if not host:host=None
                if not port:port=None
            else:
                host = s

        return user, password, host, password
