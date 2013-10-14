import re
import abc
import http.client
import urllib.parse

from collections import OrderedDict

# class Privilege(metaclass=abc.ABCMeta):
#     '''
#     http://code.google.com/p/modwsgi/wiki/AccessControlMechanisms
#     '''

#     def __init__(self, environ:dict):
#         self._env = environ

#     def __del__(self):
#         pass

#     def _user(self) -> str:
#         return self._env.get('REMOTE_USER', None)

#     def _roles(self, user:str) -> tuple:
#         if user:
#             return tuple()


class Node:
    def __init__(self, environ:dict):
        self._env = environ
        super().__init__(environ)

    def __del__(self):
        del self._env

    def get(self, env:dict) -> tuple:
        return self._w3_method('get', env)

    def head(self, env:dict) ->tuple:
        return self._w3_method('head', env)

    def post(self, env:dict) ->tuple:
        return self._w3_method('post', env)

    def put(self, env:dict) ->tuple:
        return self._w3_method('put', env)

    def delete(self, env:dict) ->tuple:
        return self._w3_method('delete', env)

    def options(self, env:dict) ->tuple:
        return self._w3_method('options', env)

    def trace(self, env:dict) ->tuple:
        return self._w3_method('trace', env)

    def _w3_render(self, mapping:dict, tmpl:str, lang:str=None, extra:dict=dict(), ref:dict=dict()):
        render_ = self._env.get('wsgi.tmpl_render', None)
        if render_:
            return render_(self._env, mapping, tmpl, lang, extra, ref)

    def _w3_reload(self, file_:str):
        reload_ = self._env.get('wsgi.tmpl_reload', None)
        if reload_:
            return reload_(self._env, file_)

    def _w3_session_register(self, data, option:dict=dict()) -> tuple:
        register = self._env.get('wsgi.session_register', None)
        if register:
            return register(self._env, data, option)

    def _w3_session_unregister(self, sessionid:int=None):
        unregister = self._env.get('wsgi.session_unregister', None)
        if unregister:
            return unregister(self._env, sessionid)

    def _w3_method(self, method:str, env:dict, prefix:str='_w3_'):
        # if not method:
        #     method = inspect.getouterframes(inspect.currentframe())[1][3]

        method = prefix+method if prefix else method

        if hasattr(self, method):
            return getattr(self, method)(env)

        return self._w3_res(501)


    def _w3_id(self, url:str, pattern=None, exist:object=None) ->str:
        '''REST URL ID, eg:/path/info/1234?a=1,b=2#bk return 1234'''
        url = url.rsplit('#', 1)[0].rsplit('?', 1)[0] # trim fragment, querystring
        id_ = url.split('/')[-2] if url.endswith('/') else url.rsplit('/', 1)[-1]

        if pattern:
            obj = re.match(pattern, id_) if isinstance(pattern, str) else pattern.match(id_)
            if not obj:
                return

        if callable(exist) and not exist(id_):
            return

        return id_
        

    def _w3_input(self) -> tuple:
        '''read wsgi.input return (content_type, data)
        type_ = {
                      'urlencode':('application/x-www-form-urlencoded'),
                      'multipart':('multipart/form-data')
                      }

      '''

        content = self._env['wsgi.input'].read(int(self._env['CONTENT_LENGTH']))
        if isinstance(content, bytes):
            content = content.decode()

        content_type = self._env['CONTENT_TYPE'].lower().split(';')[0]

        if content_type == 'application/x-www-form-urlencoded':
            content = urllib.parse.parse_qs(content)
            return (content_type, content)

        if content_type == 'multipart/form-data':
            content = urllib.parse.parse_qs(content)
            return (content_type, content)

        if content_type == 'application/json':
            content = json.loads(content)
            return (content_type, content)

        if content_type in ('application/xml', 'text/xml'):
            return (content_type, content)

        return (content_type, content)


    def _w3_res_status(self, code:int, message:str=None):
        if message:
            message = "{} {}, {}".format(code,  http.client.responses[code], message)
        else:
            message = "{} {}".format(code, http.client.responses[code])
        return message


    def _w3_res(self, status, headers:list=[], body=None) -> tuple:

        # length = 0
        # if body and isinstance(body, str):
        #     body = body.encode()
        #     length = body.__len__()

        if isinstance(status, int):
            status = self._w3_res_status(status)
        if isinstance(status, (tuple,list)):
            status = self._w3_res_status(status[0], status[1])

        # if headers:
        #     if isinstance(headers, (tuple, list)):
        #         headers = dict(headers)
        #     # headers['Content-Length'] = str(length)
        #     if 'Content-Type' not in headers:
        #         headers['Content-Type'] = 'text/html'
        #     headers = list(headers.items())
        # else:
        #     headers = [('Content-Type', 'text/html'), ('Content-Length', str(length))]
        
        type_found = False
        if headers:
            for h, v in headers:
                if 'Content-Type' == h:
                    type_found = True
                    break
        if not type_found:
            headers.append(('Content-Type', 'text/html'))

        
        #body must be a bytes instance
        body = body if body else []
        body = body if isinstance(body, list) else [body]
        body = map(lambda x: x.encode() if isinstance(x, str) else x, body)

        return status, headers, body

    def _w3_get(self, env:dict) -> tuple:
        '''overwrite http method'''

        type_ = {'html':('*/*', 'application/xml', 'application/xhtml+xml', 'application/msword', 'text/html', 'text/plain', 'text/xml'),
                      'json':('application/json', 'text/javascript', 'text/json'),
                     }


        http_accept =  self._env.get('HTTP_ACCEPT', None)
        if not http_accept:
            return self._w3_res(406)
#        method = inspect.getouterframes(inspect.currentframe())[0][3]
        method = '_w3_get'
        accepts = self._w3_negotiation(http_accept)
        for accept, q in accepts.items():
            if accept in type_['html']:
                method += '_html'
                if hasattr(self, method):
                    return getattr(self, method)(env)
                return self._w3_res(501)
            if accept in type_['json']:
                method += '_json'
                if hasattr(self, method):
                    return getattr(self, method)(env)
                return self._w3_res(501)

        return self._w3_res(406)

    def _w3_negotiation(self, neg:str) -> dict:
        # http://www.gethifi.com/blog/browser-rest-http-accept-headers
        # http://kb.mozillazine.org/Network.http.accept.default
        #'HTTP_ACCEPT': b'application/json, text/javascript, */*; q=0.01'
        #'HTTP_ACCEPT': b'application/json, text/javascript, */*'
        #'HTTP_ACCEPT': b'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
        # Accept: image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*\r\n

        d = dict(
            map(lambda x:x.split(';')
                , map(lambda x: x if 'q=' in x else x+';q=1.0'
                      , neg.split(',')
                      )
                )
            )

        do = OrderedDict(sorted(d.items(), key=lambda x:x[1], reverse=True))

        return do
