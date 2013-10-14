#https://github.com/GothAlice/wsgi2/blob/master/pep-0444.rst

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '10 Jan 2012'
__credits__ = 'no credits'

import abc

class Middleware(metaclass=abc.ABCMeta):
    '''ingeress filter'''

    def __init__(self, app):
        self._app = app

    def __call__(self, environ):
        return self._app(environ)

    def _msg(self, msg:str)->str:
        return "{},{}; {}".format(self.__module__, self.__class__.__name__, msg)

#ref www.python.org/dev/peps/pep-0444/
class SideBySide(Middleware):

    def __init__(self, app:object):
        self._app = app
    
    def __call__(self, environ):

        def func(status, headers, body):
            return status, headers, body

        def helper(app, environ, func):
            app_response = app(environ)
            if not hasattr(app_response, '__call__'):
                return func(*app_response)

        def sidebyside(app):
            def wrapper(envrion):
                return helper(app, environ, func)
            return wrapper

        return sidebyside(self._app)(environ)


class T12:
    '''wsgi 1to2'''
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, start_response):

        environ['PATH_INFO'] = environ.get('SCRIPT_NAME', '') + environ['PATH_INFO']

        # for k, v in environ.items():
        #     if isinstance(v, str):
        #         environ[k] = v.encode()

        status, headers, body =  self._app(environ)
        # print(repr(headers))

        # web3 status,headers to pep3333 encode/decode
        # if isinstance(status, bytes):
        #     status = status.decode()

        # headers = list(map(lambda x:(x[0].decode() if isinstance(x[0], bytes) else x[0], 
        #                              x[1].decode() if isinstance(x[1], bytes) else x[1])
        #                    , headers))

        start_response(status, headers)
        return body



def application(environ):
    body = repr(environ).encode()
    status = b'200 OK'    
    headers = [(b'Content-Type', b'text/plain'), (b'Content-Length', str(len(body)).encode())]

    body = repr(environ).encode()
    status = '200 OK'    
    headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(body)))]

    return status, headers, [body]

    

def application2(environ):
    body = repr(environ).encode()
    status = b'200 OK'    
    headers = [(b'Content-Type', b'text/plain')]

    def b():
        for i in range(1,10):
            yield i

    yield status, headers, b()

    # headers = [(b'Content-Type', b'text/plain'), (b'Content-Length', str(len(body)).encode())]
    # return status, headers, [body]

# import collections
# env = {}
# print(type(application2(env)))
# print(isinstance(application2(env), collections.Iterable))
# print(application2(env))
# for s,h,b in application2(env):
#     print(s)
#     print(h)
#     for i in b:
#         print(i)

