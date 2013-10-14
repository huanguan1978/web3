#!/usr/bin/env python
"""web32 middleware static dir
"""

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '08 Mar 2011'
__credits__ = 'no credits'


import os
from mimetypes import guess_type
from email.utils import parsedate, formatdate

from .middleware import Middleware

class Static(Middleware):
    '''Static(app:object, static_dir:str, path_info:str)'''
    def __init__(self, app:object, static_dir:str, path_info:str, cache_max_age:int=3600):
        self._app = app
        self._static_dir = static_dir
        self._path_info = path_info
        self._cache_max_age = cache_max_age
        
    def __call__(self, environ):
        schema, path_info, request_method = environ['wsgi.url_scheme'], environ['PATH_INFO'], environ['REQUEST_METHOD']

        if not schema.startswith('http'):
            return self._app(environ)

        req_ims = environ.get('HTTP_IF_MODIFIED_SINCE', None)

        normpath = os.path.normpath(path_info)[1:]
        if not normpath: #normpath = '/'
            return self._app(environ)

        request_method = request_method.lower()
        allow_methods = {'get', 'head', 'options'}
        if request_method not in allow_methods:
            return '405 Method Not allowd', [('Content-Length', '0'), ('Allow', ', '.join(allow_methods).upper())], []
           
        #403 Forbidden,etc environ['PATH_INFO']=/etc/passwd
        # if not os.path.normpath(os.path.join(self._static_dir, path_info)).startswith(self._static_dir):
        #     return b'403 Forbidden', [(b'Content-Length', b'0')], []

        normpath = os.path.join(os.path.expanduser(os.path.expandvars(self._static_dir)), normpath)
        if not os.path.exists(normpath):
            return '404 not found', [('Content-Length', '0')], []

        if not os.access(normpath, os.R_OK):
            return '403 Forbidden', [('Content-Length', '0')], []

        stat = os.stat(normpath)
        last_modified = formatdate(stat.st_mtime)
       
        if req_ims:
            if parsedate(req_ims) >= parsedate(last_modified):
                return '304 Not Modified', [('Content-Length', '0')], []

        if request_method == 'options':
            return '204 Not Content', [('Content-Length', '0'), ('Allow', ', '.join(allow_methods).upper())], []

        headers = []
        content_length = stat.st_size
        content_type = guess_type(normpath)[0]
        if content_type:
            headers.extend([ ('Content-Type', content_type) ])
            
        headers.extend([('Content-Length', str(stat.st_size))
                    , ('Last-Modified', last_modified)
                    , ('Cache-Control', 'must-revalidate, max-age=' + str(self._cache_max_age))
                    ])

        if request_method == 'head':
            return '204 Not Content', headers, []
        if request_method == 'get':
            return '200 OK', headers, [open(normpath, 'rb').read()]

        return self._app(environ)

        def func(status, headers, body):
            
            return status, headers, body

        def helper(app, environ, func):
            app_response = app(environ)
            if not hasattr(app_response, '__call__'):
                return func(*app_response)

            raise Exception

        def sidebyside(app):
            def wrapper(envrion):
                return helper(app, environ, func)
            return wrapper
        
        return sidebyside(self._app)(environ)
