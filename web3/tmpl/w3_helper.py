class Helper:
    def _w3_js_alert(self, text:str, location:str=None) -> str:
        '''return javascript alert
        '''
        page = '<!DOCTYPE html><html><head><meta charset="utf-8" /><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head><body></body><script id="_w3_js_alert" type="text/javascript">alert("{}");{}</script></html>'.format(text, 'location.href="{}";'.format(location) if location else '')
        return page

    def _w3_js_callback(self, code:str, src:str='', text:str='') -> str:
        '''return javascript code block
        '''
        page = '<!DOCTYPE html><html><head><meta charset="utf-8" /><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />{}</head><body>{}</body><script id="_w3_js_callback" type="text/javascript">{}</script></html>'.format(src, text, code)
        return page
