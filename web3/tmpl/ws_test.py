#!/bin/env python3

class Test:
    def __init__(self, environ:dict):
        self._env = environ
        self._dbh = self._env['wsgi.database']
        self._dbh_r = self._dbh['_rw']
        self._dbh_rw = self._dbh['_rw']
        super().__init__(environ)

    def sqlite_version(self) -> str:
        sql = 'SELECT sqlite_version()'
        return self._dbh_r.execute(sql).fetchone()
