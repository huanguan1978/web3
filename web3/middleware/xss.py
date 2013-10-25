#!/usr/bin/python
'''wsgi2 middleware anti xss
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '28 January 2011'
__credits__ = 'no credits'


import re

from urllib.parse import parse_qs
from http.client import responses

from .middleware import Middleware

class XSS(Middleware):
    '''wsgi2 middleware, anti xss 
    url limit:ref:http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url
    '''

    def __init__(self, app:object, url_limit:int=2000, entity_limit:int=8192):
        self._app = app
        self._url_length = url_limit
        self._content_length = entity_limit
        self._re_js = re.compile(
            r'<|(j\*a\*v\*a\*s\s*c\s*r\s*i\s*p\s*t\s*:)'
            ,re.IGNORECASE | re.MULTILINE)
        

    def __call__(self, environ:dict):
        schema, request_method, query_string, request_content_length, request_content_type = environ['wsgi.url_scheme'], environ['REQUEST_METHOD'], environ.get('QUERY_STRING', None), environ.get('CONTENT_LENGTH', None), environ.get('CONTENT_TYPE')

        if not schema.startswith('http'):
            return self._app(environ)

        if query_string:
            if len(query_string) > self._url_length:
                return self.__abrot(414) # '414 Request-URI Too Long'

            query_string = parse_qs(query_string)
            for key, vals in query_string.items():
                for val in vals:
                    if val:
                        if self._re_js.search(val):
                            return self.__abrot(410) # '410 Gone'

        if request_method.upper() in ('PUT', 'POST'):
            if not request_content_type:
                return self.__abrot(415) # '415 Unsupported Media Type'
            if not request_content_length:
                return self.__abrot(411) # '411 Length Required'
            
            if request_content_length > self._entity_length:
                return self.__abrot(413) # '413 Request Entity Too Large'

        if request_content_type and request_content_length:

            raw_input_ = environ['wsgi.input'].read(int(request_content_length))
            content_type = request_content_type.lower().split(';')

            if content_type in ('application/x-www-form-urlencoded', 'multipart/form-data'):
                content = parse_qs(content)

                for key, vals in qs.items():
                    for val in vals:
                        if val:
                            if self._re_js.search(val):
                                return self.__abrot(410) # '410 Gone'

        return self._app(environ)

    def __abrot(self, code:int):
        status = "{} {}".format(code,  responses[code]) 
        headers = [('Connection', 'close'), ('Content-Type','text/plain'), ('Content-Length','0')]
        body = []
        return status, headers, body
