#!/usr/bin/env python
'''wsgi2 middleware sendmail

sendmail use smtp
'''

__version__ = '$Revision $'
__author__  = 'crown.hg <crown.hg@gmail.com>'
__date__    = '16 Dec 2011'
__credits__ = 'no credits'

import os
import sys
import warnings
import time

sys.path.append(os.path.normpath(os.path.join(os.getcwd(), '../../')))

from web3.lib.mail import Smtp
from .middleware import Middleware

class Sendmail(Middleware):
    
    def __init__(self, app:object, password:str=None, username:str=None, server:str='localhost', port:int=25, replyto:str=None):
        self._app = app
        self._username = username
        self._password = password
        self._server = server
        self._port = port
        self._replyto = replyto

        if self._username is None:
            self._username = os.getlogin()

    def __call__(self, environ): 
        if not environ.get('wsgi.smtp', None):
            environ['wsgi.smtp'] = dict(sender=self._username, replyto = self._replyto)
            environ['wsgi.sendmail'] = self._sendmail

        if environ.get('wsgi.debug', None):
            msg = 'activate sendmail, smtp info, port:{}, server:{}, username:{}, password:hiddle, sender:{}, reply-to:{}'.format(
                self._port, self._server, self._username, self._username, self._replyto)
            print(self._msg(msg), file=environ['wsgi.errors'])

        return self._app(environ)

    def _sendmail(self, to, subject=None, text:str=None, html=None, attachments=None, cc=None, bcc=None):
        smtp = Smtp(self._username, self._password, self._server, self._port)
        msg = smtp.message(self._username, to, self._replyto, cc, bcc, subject, text, html, attachments)
        smtp.smtp()
        senderr = smtp.sendmessage(msg)
        del smtp

        return senderr

