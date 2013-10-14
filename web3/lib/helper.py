import re
import json
import datetime

from . import valid
from . import paginator

REGEX = {
    'digit':re.compile('\d+'),
    'isodate':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])$'),
    'isotime':re.compile('^([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?$'),
    'isodatetime':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])(\D?([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?([zZ]|([\+-])([01]\d|2[0-3])\D?([0-5]\d)?)?)?$'),

    'color':re.compile('^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})'), # eg:#FFFFFF
    'email':re.compile('[\w-]+@([\w-]+\.)+[\w-]+'),            # eg:
    'url':re.compile('^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$'),
    'month':re.compile('^(\d{4})\D?(0[1-9]|1[0-2])'),
    'week':re.compile('^(\d{4})\D?[W|w]([0-5][0-2])'),
    'float':re.compile('^[-+]?[0-9]+[.]?[0-9]*([eE][-+]?[0-9]+)?$'), # eg:Matches 123 | -123.35 | -123.35e-2
}

class Helper:
    '''web3 helper
    '''

    def __init__(self, environ):
        self._env = environ

    def _w3_dumps(self, obj, timezone:object=None):
        '''json dumps use JSONTZEncoder '''
        return json.dumps(obj, cls=JSONTZEncoder, timezone=timezone)

    def _w3_tzoffset(self, tzoffset:str='00:00,1'):
        '''timezone object by tzoffset'''
        return TZOFFSET.get(tzoffset, None)

    def _w3_regex(self, name:str) -> object:
        return REGEX[name]

    def _w3_match(self, key:str, val:str) -> bool:
        if key in REGEX:
            return self._w3_regex(key).match(val)

    def _w3_str2isodate(self, isodate:str) -> object:
        d = self._w3_match('isodate', isodate)
        if d:
            d = d.groups()
            return datetime.date(int(d[0]), int(d[1]), int(d[2]))

    def _w3_str2isotime(self, isotime:str, timezone:object=None) -> object:
        d = self._w3_match('isotime', isotime)
        if d:
            d = d.groups()
            return datetime.time(int(d[0]), int(d[1]), int(d[2]), tzinfo=timezone)

    def _w3_str2isodatetime(self, isodatetime:str, timezone:object=None) -> object:
        d = self._w3_match('isodatetime', isodatetime)
        if d:
            d = d.groups()
            return datetime.datetime(int(d[0]), int(d[1]), int(d[2]), int(d[4]), int(d[5]), int(d[6]), tzinfo=timezone)

    def _w3_input_invalid(self, attr:dict, data:dict) -> bool:
        '''
        '''
        vf = valid.VF(attr, data)
        result = vf.invalid
        del vf
        return result

    def _w3_pager(self, url:str, start:int, stop:int, step:int, theme:dict=None) -> str:
        '''
        '''
        pager = paginator.Paginator(url, start, stop, step)
        return pager.paginator(theme)


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

#
#timezone

class JSONTZEncoder(json.JSONEncoder):
    '''JSON TimeZone Encoder'''
    def __init__(self, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None
                 , timezone=None):
        self.timezone = timezone
        super().__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent, separators, default)

    
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.time, datetime.date)):
            if isinstance(obj, datetime.time):
                if obj.tzinfo and self.timezone:
                    pass
            if isinstance(obj, datetime.datetime):
                if obj.tzinfo and self.timezone:
                    obj = obj.astimezone(self.timezone)
            return obj.isoformat()

        return super().default(self, obj)


class TZOffset(datetime.tzinfo):
    '''FixedOffset '''
    def __init__(self, seconds, tzname=None):
        self._tzname = tzname
        self._offset_secs = seconds
        self._offset_mins = self._offset_secs // 60
        self._offset_timedelta = datetime.timedelta(0, self._offset_mins * 60)
        self._dst = datetime.timedelta(0)
        
    def utcoffset(self, offset_from):
        return self._offset_timedelta

    def tzname(self):
        return self._tzname

    def dst(self, arg):
        return self._dst

    def __repr__(self):
        return "{path}.{name}({off}{tzname})".format(
                path = type(self).__module__,
                name = type(self).__name__,
                off = repr(self._offset_timedelta.days * 24 * 60 * 60 + self._offset_timedelta.seconds),
                tzname = (
                        ", tzname = {tzname!r}".format(tzname = self._tzname) \
                        if self._tzname is not None else ""
                )
        )


UTC = TZOffset(0, tzname='UTC')

TZOFFSET = {
    '-12:00,0':TZOffset(-43200, tzname='(-12:00) International Date Line West'),
    '-11:00,0':TZOffset(-39600, tzname='(-11:00) Midway Island, Samoa'), 
    '-10:00,0':TZOffset(-36000, tzname='(-10:00) Hawaii'), 
    '-09:00,1':TZOffset(-32400, tzname='(-09:00) Alaska'), 
    '-08:00,1':TZOffset(-28800, tzname='(-08:00) Pacific Time (US & Canada)'), 
    '-07:00,0':TZOffset(-25200, tzname='(-07:00) Arizona'), 
    '-07:00,1':TZOffset(-25200, tzname='(-07:00) Mountain Time (US & Canada)'), 
    '-06:00,0':TZOffset(-21600, tzname='(-06:00) Central America, Saskatchewan'), 
    '-06:00,1':TZOffset(-21600, tzname='(-06:00) Central Time (US & Canada), Guadalajara, Mexico city'), 
    '-05:00,0':TZOffset(-1800,  tzname='(-05:00) Indiana, Bogota, Lima, Quito, Rio Branco'), 
    '-05:00,1':TZOffset(-18000, tzname='(-05:00) Eastern time (US & Canada)'), 
    '-04:00,1':TZOffset(-14400, tzname='(-04:00) Atlantic time (Canada), Manaus, Santiago'), 
    '-04:00,0':TZOffset(-14400, tzname='(-04:00) Caracas, La Paz'), 
    '-03:30,1':TZOffset(-12600, tzname='(-03:30) Newfoundland'), 
    '-03:00,1':TZOffset(-10800, tzname='(-03:00) Greenland, Brasilia, Montevideo'), 
    '-03:00,0':TZOffset(-10800, tzname='(-03:00) Buenos Aires, Georgetown'), 
    '-02:00,1':TZOffset(-7200,  tzname='(-02:00) Mid-Atlantic'), 
    '-01:00,1':TZOffset(-3600,  tzname='(-01:00) Azores'), 
    '-01:00,0':TZOffset(-3600,  tzname='(-01:00) Cape Verde Is.'), 
    '00:00,0':TZOffset(0, tzname='(00:00) Casablanca, Monrovia, Reykjavik'), 
    '00:00,1':TZOffset(0, tzname='(00:00) GMT: Dublin, Edinburgh, Lisbon, London'), 
    '+01:00,1':TZOffset(3600, tzname='(+01:00) Amsterdam, Berlin, Rome, Vienna, Prague, Brussels'), 
    '+01:00,0':TZOffset(3600, tzname='(+01:00) West Central Africa'), 
    '+02:00,1':TZOffset(7200, tzname='(+02:00) Amman, Athens, Istanbul, Beirut, Cairo, Jerusalem'), 
    '+02:00,0':TZOffset(7200, tzname='(+02:00) Harare, Pretoria'), 
    '+03:00,1':TZOffset(10800, tzname='(+03:00) Baghdad, Moscow, St. Petersburg, Volgograd'), 
    '+03:00,0':TZOffset(10800, tzname='(+03:00) Kuwait, Riyadh, Nairobi, Tbilisi'), 
    '+03:30,0':TZOffset(12600, tzname='(+03:30) Tehran'), 
    '+04:00,0':TZOffset(14400, tzname='(+04:00) Abu Dhadi, Muscat'), 
    '+04:00,1':TZOffset(14400, tzname='(+04:00) Baku, Yerevan'), 
    '+04:30,0':TZOffset(16200, tzname='(+04:30) Kabul'), 
    '+05:00,1':TZOffset(18000, tzname='(+05:00) Ekaterinburg'), 
    '+05:00,0':TZOffset(18000, tzname='(+05:00) Islamabad, Karachi, Tashkent'), 
    '+05:30,0':TZOffset(19800, tzname='(+05:30) Chennai, Kolkata, Mumbai, New Delhi, Sri Jayawardenepura'), 
    '+05:45,0':TZOffset(20700, tzname='(+05:45) Kathmandu'), 
    '+06:00,0':TZOffset(21600, tzname='(+06:00) Astana, Dhaka'), 
    '+06:00,1':TZOffset(21600, tzname='(+06:00) Almaty, Nonosibirsk'), 
    '+06:30,0':TZOffset(23400, tzname='(+06:30) Yangon (Rangoon)'), 
    '+07:00,1':TZOffset(25200, tzname='(+07:00) Krasnoyarsk'), 
    '+07:00,0':TZOffset(25200, tzname='(+07:00) Bangkok, Hanoi, Jakarta'), 
    '+08:00,0':TZOffset(28800, tzname='(+08:00) Beijing, Hong Kong, Singapore, Taipei'), 
    '+08:00,1':TZOffset(28800, tzname='(+08:00) Irkutsk, Ulaan Bataar, Perth'), 
    '+09:00,1':TZOffset(32400, tzname='(+09:00) Yakutsk'), 
    '+09:00,0':TZOffset(32400, tzname='(+09:00) Seoul, Osaka, Sapporo, Tokyo'), 
    '+09:30,0':TZOffset(34200, tzname='(+09:30) Darwin'), 
    '+09:30,1':TZOffset(34200, tzname='(+09:30) Adelaide'), 
    '+10:00,0':TZOffset(36000, tzname='(+10:00) Brisbane, Guam, Port Moresby'), 
    '+10:00,1':TZOffset(36000, tzname='(+10:00) Canberra, Melbourne, Sydney, Hobart, Vladivostok'), 
    '+11:00,0':TZOffset(39600, tzname='(+11:00) Magadan, Solomon Is., New Caledonia'), 
    '+12:00,1':TZOffset(43200, tzname='(+12:00) Auckland, Wellington'), 
    '+12:00,0':TZOffset(43200, tzname='(+12:00) Fiji, Kamchatka, Marshall Is.'), 
    '+13:00,0':TZOffset(46800, tzname='(+13:00) Nuku\'alofa'), 
}
