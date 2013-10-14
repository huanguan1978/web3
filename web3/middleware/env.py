#!/usr/bin/env python
''' web3 middleware setenvif    
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '08 Mar 2011'
__credits__ = 'no credits'


class Env:
    def __init__(self, app:object, hook:object=None):
        self._app  = app
        self._hook = hook

    def __call__(self, environ):
        if self._hook:
            environ = self._hook(environ)

        if environ.get('wsgi.debug', None):
            msg = "{},{}; hook:{}".format(
                    self.__module__, self.__class__.__name__,
                    self._hook.__name__ if self._hook else None
                    )
            print(msg, file=environ['wsgi.errors'])

        return self._app(environ)
