#!/usr/bin/env python
'''
wsgi2 middleware gzip mime ^html/ and ^application/ content
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '19 January 2012'
__credits__ = 'no credits'

from io import BytesIO
from gzip import GzipFile

from .middleware import SideBySide

class Zip(SideBySide):

    def __init__(self, app:object, minlength:int=2048, compresslevel:int=6):
        self._app = app
        self._minlength = minlength
        self._compresslevel = compresslevel

    def __call__(self, environ):
        schema, request_method, http_accept_encoding = environ['wsgi.url_scheme'], environ['REQUEST_METHOD'],  environ.get('HTTP_ACCEPT_ENCODING', None)
        if not schema.startswith('http'):
            return self._app(environ)
        if 'get' != request_method.lower():
            return self._app(environ)
        if not http_accept_encoding or 'gzip' not in http_accept_encoding:
            return self._app(environ)

        if environ.get('wsgi.debug', None):
            msg = "min length:{}, compress level:{}".format(self._minlength, self._compresslevel)
            print(self._msg(msg), file=environ['wsgi.errors'])

        
        def func(status, headers, body):
            if not body or int(status[:3]) in (101, 102, 204, 205, 304):
                return status, headers, body

            content_type = None
            content_length_header = None
            vary_header = None
            for header in headers:
                h = header[0].lower()
                if 'content-encoding' == h:
                    return status, headers, body
                if 'content-length' == h:
                    if int(header[1]) < self._minlength:
                        return status, headers, body
                    content_length_header = header
                    continue
                if 'content-type' == h:
                    content_type = header[1].lower()
                    continue
                if 'vary' == h:
                    vary_header = header

            if content_type and (content_type.startswith('text/') or content_type.startswith('application/')):
                if content_length_header:
                    headers.remove(content_length_header)
                #vary accept-encoding, not vary conent-encoding firefox content encoding error 
                varys = list()
                if vary_header:
                    varys = vary_header[1].lower().split(',')
                for vary in ('Accept-Encoding', 'Content-Encoding'):
                    if vary not in varys:
                        varys.append(vary)
                vary_header = ('Vary', ','.join(varys))

                buf = BytesIO()
                output = GzipFile(mode='wb', compresslevel=self._compresslevel, fileobj=buf)
                for content in body:
                    output.write(content)
                else:
                    output.close()

                buf.seek(0)
                content = buf.getvalue()
                buf.close()
                headers.append(('Content-Encoding', 'gzip'))
                headers.append(('Content-Length', str(len(content))))
                headers.append(vary_header)
                body = [content]

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
