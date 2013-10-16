#!/bin/env python3

from ..w3.tmpl import head, nav, header, footer

class Test:
    def __init__(self, environ):
        super().__init__(environ)

        
    def _w3_get_html(self, environ):
        env = environ
        remote_user, remote_role = env.get('REMOTE_USER', None), env.get('REMOTE_ROLE', None)

        lang = None
        extra = dict()

        mapping = dict(
            nav = nav(remote_user, remote_role),
            head = head(),
            header = header(),
            footer = footer(),
            title = 'test page',
            )

        outputs = self._w3_render(mapping, '\\test\\test.html', lang, extra)
        if outputs:
            body, headers = outputs
            return self._w3_res(200, headers, body=[body])

        return self._w3_res(204)
