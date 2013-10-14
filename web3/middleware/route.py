#!/usr/bin/python
'''wsgi2 middleware route

dispatch based on the environ['PATH_INFO']
transfer http path_info segment to class attribute
transfer http request_method to some name class function

EXAMPLE

class Node:
    def __init__(self, environ):
        self._env = environ

class Base(Node):
    def get(self):
        body = b'base page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]

class Private(Node):
    def get(self):
        body = b'private page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]

class Verification(Node):
    def get(self):
        body = b'verification page'
        status = b'200 ok'
        headers = [(b'Content-Type', b'text/plain')]
        return status, headers, [body]


def application(envrion):
    pass

env = dict()
urls = [
(0, '.*', '^/', Index, dict()),
(0, '^image', '^/', Image, dict()),
(1, '.*', '^/private', Private, dict(get=(), post=(), delete=()) ),
]
app = Route(app, urls)
'''


__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '28 January 2011'
__credits__ = 'no credits'

import re
from operator import methodcaller

from .middleware import Middleware

class Route(Middleware):
    '''wsgi2 middleware, path_info  http_request to request_method'''

    methods = {'get', 'put', 'post', 'delete', 'head', 'options', 'connect', 'trace'}
    def __init__(self, app:object, urls:list, slash:bool=True, authenticate:bool=False):
        self._app = app
        self._urls = urls
        self._slash = slash
        self._authc = authenticate

    def __call__(self, environ):
        schema, host, path_info, request_method = environ['wsgi.url_scheme'], environ['HTTP_HOST'], environ['PATH_INFO'], environ['REQUEST_METHOD']

        if not schema.startswith('http'):
            return self._app(environ)

        if -1 != path_info.find('.'): #static file
            return self._app(environ)

        if self._slash and not path_info.endswith('/'):
            path_info += '/'

        request_method = request_method.lower()
        for tls, host_pattern, path_pattern, cls, acl in self._urls:

            re_match_host_object = host_pattern.match(host)
            re_match_path_object = path_pattern.match(path_info)
            if re_match_host_object and re_match_path_object:

                if bool(tls):
                    if 'https' != schema:
                        return '403 Forbidden', [('Content-Length', '0')], []

                if self._authc and acl and request_method in acl:
                    if not environ.get('REMOTE_USER', None):
                        return '403 Forbidden', [('Content-Length', '0')], []

                allow_methods = self.methods.intersection(dir(cls))
                if request_method in allow_methods:

                    if environ.get('wsgi.debug', None):
                        msg = "{},{};{},{},{},{},{}".format(cls, request_method, request_method
                                                            , host, host_pattern.pattern, path_info, path_pattern.pattern)
                        print(self._msg(msg), file=environ['wsgi.errors'])

#                    return methodcaller(request_method)(cls(environ))
                    return methodcaller(request_method
                                        , environ
                                        , *re_match_path_object.groups()
                                        , **re_match_path_object.groupdict()
                                        )(cls(environ))

                return '405 Method Not allowd', [('Content-Length', '0'), ('Allow', ', '.join(allow_methods).upper())], []

        if environ.get('wsgi.debug', None):
            msg = "{},{} not found! return self._app(envrion)".format(request_method, path_info)
            print(self._msg(msg), file=environ['wsgi.errors'])

        return self._app(environ)
        return '404 not found', [('Content-Length', '0')], []
