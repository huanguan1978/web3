#!/usr/bin/env python
'''wsgi2 middleware template

template some string.Template

'''
__author__  = 'crown.hg <crown.hg@gmail.com>'
__version__ = '$Revision $'
__date__    = '29 Dec 2011'
__credits__ = 'no credits'

import os
import re
import json
import warnings

from string import Template
from collections import OrderedDict, defaultdict

from .middleware import Middleware

class Tmpl(Middleware):
    def __init__(self, app:object, path:str, lang:str='zh', watch:bool=True):
        self._app = app
        self._path = os.path.expandvars(os.path.expanduser(os.path.normpath(path)))
        self._tmpl_postfix = 'html'
        self._lang_postfix = 'json.js'
        self._lang_pattern = '=\s*({.*})'
        self._lang_default = lang
        self._watch = watch
        self._tmpl = dict()
        self._lang = dict()

        self._load()

    def __call__(self, environ):
        if not environ.get('wsgi.tmpl', None):
            # environ['wsgi.tmpl_self'] = self
            environ['wsgi.tmpl'] = self._tmpl
            environ['wsgi.tmpl_path'] = self._path
            environ['wsgi.tmpl_postfix'] = self._tmpl_postfix
            environ['wsgi.tmpl_reload'] = self.reload
            environ['wsgi.tmpl_render'] = self.render


        if not environ.get('wsgi.lang', None):
            # environ['wsgi.lang_self'] = self
            environ['wsgi.lang'] = self._lang
            environ['wsgi.lang_path'] = self._path
            environ['wsgi.lang_default'] = self._lang_default
            environ['wsgi.lang_postfix'] = self._lang_postfix
            environ['wsgi.lang_pattern'] = self._lang_pattern
            # environ['wsgi.lang_reference'] = self.reference

        if environ.get('wsgi.debug', None):
            msg = "activate tmpls:{}".format(','.join(self._tmpl.keys()))
            print(self._msg(msg), file=environ['wsgi.errors'])
            msg = "activate langs:{}".format(','.join(self._lang.keys()))
            print(self._msg(msg), file=environ['wsgi.errors'])

        return self._app(environ)

    def _load(self):
        '''load template and language'''
        length = len(self._path)
        for root, dirs, files in os.walk(self._path):
            for filename in files:
                if filename.endswith((self._tmpl_postfix, self._lang_postfix)):
                    absfile = os.path.join(root, filename)
                    filename = absfile[length:]

                    if filename.endswith(self._tmpl_postfix):
                        tmpl_obj =self._load_tmpl(absfile, self._watch)
                        if tmpl_obj:
                            self._tmpl[filename] = tmpl_obj

                    if filename.endswith(self._lang_postfix):
                        lang_obj = self._load_lang(absfile, self._watch)
                        if lang_obj:
                            self._lang[filename] = lang_obj


    def _load_tmpl(self, absfile:str, watch:bool=False)->dict:
        obj = dict()
        try:
            fd = open(absfile, 'r')
            mtime = os.stat(absfile).st_mtime
        except EnvironmentError as e:
            raise
        else:
            obj = {
                'object': Template(fd.read()),
                'file'  : absfile,
                'mtime' : mtime,
                'watch' : watch,
                }
        finally:
            fd.close()

        return obj


    def _load_lang(self, absfile:str, watch:bool=False)->dict:
        obj = dict()
        try:
            fd = open(absfile, 'r')
            mtime = os.stat(absfile).st_mtime
        except EnvironmentError as e:
            raise
        else:
            obj = {
                'object': None,
                'file'  : absfile,
                'mtime' : mtime,
                'watch' : watch,
                }
            try:
                re_match_obj = re.search(self._lang_pattern, fd.read(), re.DOTALL)
            except KeyError as e:
                raise
            else:
                if re_match_obj:
                    try:
                        obj['object'] = json.loads(re_match_obj.groups()[0])
                    except ValueError:
                        raise
                else:
                    warnings.warn('not exists re match object from re lang pattern')
            finally:
                re_match_obj = None
        finally:
            fd.close()

        return obj


    @staticmethod
    def reload(environ:dict, file_:str):

        if file_:
            tmpl_postfix = environ['wsgi.tmpl_postfix']
            lang_postfix = environ['wsgi.lang_postfix']

            if file_.endswith((tmpl_postfix, lang_postfix)):

                attr = dict()
                if file_.endswith(tmpl_postfix):
                    attr = environ['wsgi.tmpl'][file_]
                if file_.endswith(lang_postfix):
                    attr = environ['wsgi.lang'][file_]

                if not attr.get('watch', None):
                    return attr.get('object', None)

                mtime = attr.get('mtime', None)
                if mtime:
                    absfile = attr.get('file', None)
                    if absfile:
                        lmtime = os.stat(absfile).st_mtime

                        if lmtime == mtime:
                            return attr.get('object', None)

                        obj = None
                        attr['mtime'] = lmtime
                        try:
                            fd = open(absfile, 'r')
                        except EnvironmentError as e:
                            raise
                        else:
                            if absfile.endswith(tmpl_postfix):
                                try:
                                    obj = Template(fd.read())
                                except Exception as e:
                                    raise
                                else:
                                    attr['object'] = obj
                                    environ['wsgi.tmpl'][file_] = attr

                            if absfile.endswith(lang_postfix):
                                re_pattern = environ.get('wsgi.lang_pattern', None)
                                try:
                                        re_match_obj = re.search(re_pattern, fd.read(), re.DOTALL)
                                except KeyError:
                                    raise
                                else:
                                    if re_match_obj:
                                        try:
                                            obj = json.loads(re_match_obj.groups()[0])
                                        except ValueError:
                                            raise
                                        else:
                                            attr['object']=obj
                                            environ['lang'][file_] = attr
                                    else:
                                        warnings.warn('not exists re match object from re lang pattern')
                                finally:
                                    re_match_obj = None
                        finally:
                            fd.close()

                        return obj

    @staticmethod
    def render(environ:dict, mapping:dict, tmpl:str, lang:str=None, extra:dict=dict(), ref:dict=dict()) -> str:
        '''mapping:dict = mapping.update(extra); mapping.replace(ref[k], ref[v])'''

        reload_ = environ.get('wsgi.tmpl_reload', None)
        if not reload_:
            reload_ = Tmpl.reload

        obj_tmpl = reload_(environ, tmpl)
        obj_lang = reload_(environ, lang)
        headers = list()

        if obj_tmpl and obj_lang:
            lang_found = environ.get('wsgi.lang_default', None)
            lang_accept = environ.get('HTTP_ACCEPT_LANGUAGE', None)

            if lang_accept:
                lang_neg = OrderedDict(
                    sorted(
                        dict(
                            map(lambda x:x.split(';')
                                , map(lambda x: x if 'q=' in x else x+';q=1.0'
                                      , lang_accept.split(',')
                                      )
                                )
                            ).items()
                        ,key=lambda x:x[1], reverse=True
                        )
                    )

                for accept, q in lang_neg.items():
                    if accept in obj_lang:
                        lang_found = accept
                        break

            if lang_found in obj_lang:
                headers = [('Content-Langage', lang_found), ('Vary', 'Accept-Language')]
                mapping.update(obj_lang[lang_found])

                if lang_found in extra:
                    mapping.update(extra[lang_found])

        if obj_tmpl:
            if extra:
                mapping.update(extra)
            if ref:
                for k, v in ref.items():
                    if k in mapping and v in mapping:
                        mapping[k] = mapping[v]
            return (obj_tmpl.safe_substitute(mapping), headers)
