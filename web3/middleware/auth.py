#!/usr/bin/env python
'''
    Authenticate:验证

    
    验证扩展函数处理流程如下：
        1、从客户端请求中获取用户名和密码
        2、检验当前用户是否是当前资源授权操作组成员
        3、如果是此组成员，则检查口今是否有效,口今为兼容基本认证和消息摘要认证的MD5字符串
    
    安全注解：
        basic认证，只是用BASE64编码和解码用户名和密码，并没有处理realm信息
        digest认让，是domain项定义了一个可以获得客户端用户标识的未保护的资源。

    提示：
        chromium的domain处理，非response uri的，但在domain中出现的一定要在结尾加'/'
        如：domain = /private /private/verification
        若在uri = /private/verification检证成功，
        而客户端在uri = /private请求中并不会附上http auth信息，然而uri=/private/则会附上http auth信息
http://en.wikipedia.org/wiki/Digest_access_authentication              
'''

__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '29 Dec 2011'
__credits__ = 'no credits'


import time
import hashlib

from .middleware import Middleware

class AuthDigest(Middleware):
    '''
        A1 = md5(username:realm:password)
        A2 = md5(request-method:uri) // request method = GET, POST, etc.
        Hash = md5(A1:nonce:nc:cnonce:qop:A2)
        if Hash == response:
            pass   //success!
        else:
            pass   //failure!
    '''

    
    def __init__(self, app:object, get_passwd:object, get_realm:object, path:str, domain:str, has_md5a1passwd:bool=False):
        #~ get_passwd 为认证所需的用户密码， location 为认证成功后返回的响应信息
        #~ path 为需要验证授权URI， domain 为http header验证信息附加区域
        self._app = app
        self._path = path
        self._domain = domain #"{} {}".format(domain, path)
        self._has_md5a1passwd = has_md5a1passwd

        self._get_passwd = get_passwd
        self._get_realm = get_realm

    def __call__(self, environ):
        schema, path_info, request_method = environ['wsgi.url_scheme'], environ['PATH_INFO'], environ['REQUEST_METHOD']

        if not schema.startswith('http'):
            return self._app(environ)

        remote_user = environ.get('REMOTE_USER', None)
        if remote_user:
            return self._app(environ)


        realm = self._get_realm(environ, None)
        auth_header = environ.get('HTTP_AUTHORIZATION', None)
        if path_info.startswith(self._path) or path_info.startswith(self._domain):
            if auth_header:
                req_digest = self.digest2dict(auth_header)

                req_username = req_digest['Digest username']
                realm = self._get_realm(environ, req_username)

                password = self._get_passwd(environ, req_username, realm)
                if password:
                    a1 = password
                    if not self._has_md5a1passwd:
                        a1 = self.a1(req_username, realm, password)

                    a2 = self.a2(request_method, req_digest['uri'])
                    nonce = self.nonce(req_digest)
                    digest = self.digest(a1, nonce, a2, self._has_md5a1passwd)

                    if environ.get('wsgi.debug', None):
                        msg = ";a1:{},a2:{},digest:{},response:{}".format(a1, a2, digest, req_digest['response'])
                        print(self._msg(msg), file=environ['wsgi.errors'])

                    if digest == req_digest['response']:
                        environ['REMOTE_USER'] = req_username;
                        return self._app(environ)

            return self._unauthorized(realm, self.unique(), self._domain)

        return self._app(environ)
        

    def digest(self, a1:str, nonce:str, a2:str, has_md5a1:bool=False, has_md5a2:bool=False)->str:
        '''my digest Hash = md5(A1:nonce:A2)'''

        if not has_md5a1:
            a1 = self.h(a1)
        if not has_md5a2:
            a2 = self.h(a2)

        data = "{}:{}:{}".format(a1, nonce, a2)
        return self.h(data)

    def digest2dict(self, digest:str)->dict:
        '''digest auth header to dict '''
        return dict([i.split('=', 1) for i in digest.replace('"', '').split(',')])
        return dict([i.split('=', 1) for i in digest.replace('"', '').split(', ')])

    def nonce(self, req_digest:dict) ->str:
        d = req_digest
        nonce = d['nonce']
        if 'qop' in d:
            if 'cnonce' in d and 'nc' in d:
                if d['qop'].lower() in ('auth', 'auth_int'):
                    nonce = "{}:{}:{}:{}".format(d['nonce'], d['nc'], d['cnonce'], d['qop'])
        return nonce
        

    def unique(self):
        return hashlib.md5(str(time.time()).encode()).hexdigest()
        
    def _bad_request(self):
        return '400 Bad Request', [('Content-Length', '0')], []

    def _unauthorized(self, realm, nonce, domain):
        value = 'Digest realm="{}", nonce="{}", domain="{}", qop="auth"'.format(realm, nonce, domain)
        return '401 Unauthorized', [('WWW-Authenticate', value), ('Content-Length', '0')], []
       
    def a1(self, username, realm, password):
        '''HA1=MD5(A1) = MD5(username:realm:password)'''
        return "{}:{}:{}".format(username, realm, password)
        
    def a2(self, request_method, uri):
        '''HA2=MD5(A2) = MD5(method:digestURI)'''
        return "{}:{}".format(request_method, uri)
        
    def h(self, data):
        if not isinstance(data, bytes):
            data = data.encode()
        return hashlib.md5(data).hexdigest()
