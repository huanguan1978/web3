#!/usr/bin/env python
'''
    auth external
    Authorization:授权

    
    授权检查
    1、访问指定URI资源方案是否已授权
    2、当前角色当前访问方法在当前URI资源是否已授权

'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '28 January 2011'
__credits__ = 'no credits'


import re

from .middleware import Middleware

class AuthZ(Middleware):
    def __init__(self, app:object, path:str, acls:list, get_role:object):
        self._app = app
        self._path = path
        self._acls = acls
        self._get_role = get_role

    def __call__(self, environ):
        schema, host, path_info, request_method = environ['wsgi.url_scheme'], environ['HTTP_HOST'], environ['PATH_INFO'], environ['REQUEST_METHOD']

        if not schema.startswith('http'):
            return self._app(environ)

        if path_info.startswith(self._path):
            remote_user = environ.get('REMOTE_USER', None)
            if not remote_user:
                return '403 Forbidden', [('Content-Length', '0')], []

            request_method = request_method.lower()
            for tls, host_pattern, path_pattern, cls, acl in self._acls:
                if acl and acl.get(request_method, None) and path_pattern.match(path_info) and host_pattern.match(host):
                    remote_role = self._get_role(environ, remote_user)
                    environ['REMOTE_ROLE'] = remote_role
                    if environ.get('wsgi.debug', None):
                        msg = "remote_user:{},remote_role:{},request_method:{},authz_roles:{}".format(
                                remote_user, remote_role, request_method, acl[request_method])
                        print(self._msg(msg), file=environ['wsgi.errors'])

                    if remote_role in acl[request_method]:
                        return self._app(environ)
                            
                    return '403 Foribidden', [('Content-Length', '0')], []

        return self._app(environ)                
